"""
Diagnostic script: prints the cosine distance between every pair of faces in the database.
This helps us find the correct threshold to separate different people.
"""
import numpy as np
from sqlalchemy import text
from app.database import SessionLocal

def diagnose():
    db = SessionLocal()
    try:
        # Fetch all faces with their embeddings and image info
        results = db.execute(text("""
            SELECT f.id, f.person_id, f.image_id, f.embedding::text,
                   i.original_filename
            FROM faces f
            JOIN images i ON i.id = f.image_id
            ORDER BY i.uploaded_at
        """)).fetchall()

        if len(results) < 2:
            print(f"Only {len(results)} face(s) in database. Need at least 2 for comparison.")
            return

        print(f"Found {len(results)} faces in the database.\n")

        # Parse embeddings
        faces = []
        for r in results:
            emb_str = r.embedding.strip("[]")
            emb = np.array([float(x) for x in emb_str.split(",")])
            faces.append({
                "id": str(r.id)[:8],
                "person_id": str(r.person_id)[:8] if r.person_id else "None",
                "filename": r.original_filename,
                "embedding": emb,
                "norm": np.linalg.norm(emb),
            })

        # Print face info
        print("=== Face Embeddings ===")
        for f in faces:
            print(f"  Face {f['id']}  |  Person: {f['person_id']}  |  File: {f['filename']}  |  L2 Norm: {f['norm']:.4f}")
        print()

        # Compute all pairwise distances
        print("=== Pairwise Cosine Distances ===")
        print(f"{'Face A':<30} {'Face B':<30} {'Cosine Dist':>12} {'L2 Dist':>10} {'Same Person?':>14}")
        print("-" * 100)

        for i in range(len(faces)):
            for j in range(i + 1, len(faces)):
                a = faces[i]["embedding"]
                b = faces[j]["embedding"]

                # Cosine distance
                cos_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
                cos_dist = 1.0 - cos_sim

                # L2 distance (for reference)
                l2_dist = np.linalg.norm(a - b)

                # Current threshold check
                same = "YES" if cos_dist < 0.14 else "NO"

                name_a = faces[i]["filename"][:28]
                name_b = faces[j]["filename"][:28]
                print(f"  {name_a:<28} {name_b:<28} {cos_dist:>12.6f} {l2_dist:>10.4f} {same:>14}")

        print()
        print("=== Threshold Analysis ===")
        print("If two faces are DIFFERENT people but show 'YES' above, the threshold is too loose.")
        print("If two faces are the SAME person but show 'NO' above, the threshold is too strict.")
        print(f"\nCurrent threshold: 0.14")

    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
