from typing import Optional, List
from uuid import UUID

import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.models import Face, Person
from app.config import settings


class ClusteringService:
    """
    Handles auto-assignment of detected faces to person clusters.

    Strategy: CENTROID-BASED CLUSTERING with COSINE DISTANCE
    - For each new face, compute the centroid (average embedding) of each existing person.
    - Compare the new face against each person's centroid using cosine distance.
    - If the nearest centroid distance < threshold → assign to that person.
    - If no match → create a new person cluster.

    Why centroid instead of nearest-neighbor:
    - Nearest-neighbor suffers from "chaining": a bad photo in a cluster can attract
      unrelated faces, causing the cluster to drift over time.
    - Centroid averaging smooths out noise from individual photos (bad lighting, angles).
    - A new face must be similar to the AVERAGE identity, not just one outlier photo.

    Uses pgvector's cosine distance operator (<=>) for ArcFace normalized embeddings.
    """

    @staticmethod
    def assign_face_to_person(db: Session, face: Face) -> Person:
        """
        Find or create a person for the given face based on centroid similarity.

        Args:
            db: Database session.
            face: Face object with embedding already set.

        Returns:
            The Person object the face was assigned to.
        """
        # Compare against centroids of all existing persons
        nearest = ClusteringService._find_nearest_person_centroid(db, face.embedding, face.id)

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
    def _find_nearest_person_centroid(
        db: Session,
        query_embedding: list,
        exclude_face_id: Optional[UUID] = None,
    ) -> Optional[dict]:
        """
        Find the nearest person by comparing against the CENTROID (average embedding)
        of each person's face cluster.

        This is more robust than nearest-single-face because:
        - It smooths out noise from individual bad photos
        - It prevents the "chaining effect" where one outlier face pulls in unrelated faces
        - The centroid represents the average identity, not an edge case

        Returns:
            Dict with 'person_id', 'distance' or None.
        """
        embedding_arr = np.array(query_embedding)

        # Get all persons that have at least one face
        persons_with_faces = (
            db.query(Person.id)
            .join(Face, Face.person_id == Person.id)
            .distinct()
            .all()
        )

        if not persons_with_faces:
            return None

        best_match = None
        best_distance = float("inf")

        for (person_id,) in persons_with_faces:
            # Get all face embeddings for this person
            exclude_clause = ""
            params = {"person_id": str(person_id)}

            if exclude_face_id:
                exclude_clause = "AND f.id != :exclude_id"
                params["exclude_id"] = str(exclude_face_id)

            face_rows = db.execute(
                text(f"""
                    SELECT f.embedding::text
                    FROM faces f
                    WHERE f.person_id = :person_id
                    {exclude_clause}
                """),
                params,
            ).fetchall()

            if not face_rows:
                continue

            # Compute the centroid (mean of all embeddings)
            embeddings = []
            for row in face_rows:
                emb_str = row.embedding.strip("[]")
                emb = np.array([float(x) for x in emb_str.split(",")])
                embeddings.append(emb)

            centroid = np.mean(embeddings, axis=0)

            # Compute cosine distance from query to centroid
            # For L2-normalized vectors: cosine_sim = dot(a, b), cosine_dist = 1 - cosine_sim
            cosine_sim = float(np.dot(embedding_arr, centroid) / (
                np.linalg.norm(embedding_arr) * np.linalg.norm(centroid)
            ))
            distance = 1.0 - cosine_sim

            if distance < best_distance:
                best_distance = distance
                best_match = {
                    "person_id": person_id,
                    "distance": distance,
                }

        return best_match

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
        Uses cosine distance to individual faces for search results.

        Returns:
            List of dicts with 'face_id', 'image_id', 'person_id', 'distance'.
        """
        if threshold is None:
            threshold = settings.FACE_MATCH_THRESHOLD

        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        query = text("""
            SELECT f.id as face_id, f.image_id, f.person_id,
                   f.embedding <=> :embedding AS distance
            FROM faces f
            WHERE f.embedding <=> :embedding < :threshold
            ORDER BY f.embedding <=> :embedding
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
