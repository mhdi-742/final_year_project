from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import Face, Person
from app.config import settings


class ClusteringService:
    """
    Handles auto-assignment of detected faces to person clusters.

    Strategy:
    - For each new face, search the DB for the nearest existing face (by L2 distance).
    - If distance < threshold → assign to the same person.
    - If no match → create a new person cluster.

    Uses pgvector's L2 distance operator (<->) for efficient nearest-neighbor search.
    """

    @staticmethod
    def assign_face_to_person(db: Session, face: Face) -> Person:
        """
        Find or create a person for the given face based on embedding similarity.

        Args:
            db: Database session.
            face: Face object with embedding already set.

        Returns:
            The Person object the face was assigned to.
        """
        # Search for the nearest existing face using pgvector L2 distance
        nearest = ClusteringService._find_nearest_face(db, face.embedding, face.id)

        if nearest and nearest["distance"] < settings.FACE_MATCH_THRESHOLD:
            # Match found — assign to existing person
            person = db.query(Person).filter(Person.id == nearest["person_id"]).first()

            if person:
                face.person_id = person.id
                person.face_count += 1
                person.updated_at = face.created_at
                db.flush()
                return person

        # No match — create a new person cluster
        person = ClusteringService._create_new_person(db)
        face.person_id = person.id
        person.face_count = 1
        db.flush()
        return person

    @staticmethod
    def _find_nearest_face(
        db: Session,
        query_embedding: list,
        exclude_face_id: Optional[UUID] = None,
    ) -> Optional[dict]:
        """
        Find the nearest face in the database using pgvector L2 distance.

        Returns:
            Dict with 'face_id', 'person_id', 'distance' or None.
        """
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        # Build query — exclude the current face and only consider faces with a person
        exclude_clause = ""
        if exclude_face_id:
            exclude_clause = f"AND f.id != '{exclude_face_id}'"

        query = text(f"""
            SELECT f.id as face_id, f.person_id, f.embedding <-> :embedding AS distance
            FROM faces f
            WHERE f.person_id IS NOT NULL
            {exclude_clause}
            ORDER BY f.embedding <-> :embedding
            LIMIT 1
        """)

        result = db.execute(query, {"embedding": embedding_str}).fetchone()

        if result:
            return {
                "face_id": result.face_id,
                "person_id": result.person_id,
                "distance": result.distance,
            }

        return None

    @staticmethod
    def _create_new_person(db: Session) -> Person:
        """Create a new person with an auto-generated label."""
        # Count existing persons to generate a label
        count = db.query(Person).count()
        label = f"Person {count + 1}"

        person = Person(label=label)
        db.add(person)
        db.flush()  # Get the generated ID
        return person

    @staticmethod
    def find_matching_faces(
        db: Session,
        query_embedding: list,
        threshold: Optional[float] = None,
        limit: int = 50,
    ) -> List[dict]:
        """
        Find all faces matching a query embedding within the distance threshold.

        Returns:
            List of dicts with 'face_id', 'image_id', 'person_id', 'distance'.
        """
        if threshold is None:
            threshold = settings.FACE_MATCH_THRESHOLD

        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        query = text("""
            SELECT f.id as face_id, f.image_id, f.person_id,
                   f.embedding <-> :embedding AS distance
            FROM faces f
            WHERE f.embedding <-> :embedding < :threshold
            ORDER BY f.embedding <-> :embedding
            LIMIT :limit
        """)

        results = db.execute(
            query,
            {"embedding": embedding_str, "threshold": threshold, "limit": limit},
        ).fetchall()

        return [
            {
                "face_id": r.face_id,
                "image_id": r.image_id,
                "person_id": r.person_id,
                "distance": r.distance,
            }
            for r in results
        ]
