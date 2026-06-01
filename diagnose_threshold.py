"""
Targeted diagnostic: Shows same-person vs different-person L2 distances
to find the optimal threshold.
"""
import numpy as np
from sqlalchemy import text
from app.database import SessionLocal

def diagnose():
    db = SessionLocal()
    try:
        results = db.execute(text("""
            SELECT f.id, f.person_id, f.image_id, f.embedding::text,
                   i.original_filename
            FROM faces f
            JOIN images i ON i.id = f.image_id
            ORDER BY i.original_filename, f.id
        """)).fetchall()

        print(f"Total faces in database: {len(results)}\n")

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
            })

        # Print all faces with their person assignments
        print("=== All Faces ===")
        for i, f in enumerate(faces):
            print(f"  [{i}] Person={f['person_id']} | File: {f['filename']}")
        print()

        # Compute ALL pairwise L2 distances
        all_distances = []
        for i in range(len(faces)):
            for j in range(i + 1, len(faces)):
                a = faces[i]["embedding"]
                b = faces[j]["embedding"]
                l2 = float(np.linalg.norm(a - b))
                all_distances.append({
                    "i": i, "j": j,
                    "file_a": faces[i]["filename"][:35],
                    "file_b": faces[j]["filename"][:35],
                    "l2": l2,
                })

        # Sort all distances
        all_distances.sort(key=lambda x: x["l2"])

        print("=== ALL Pairwise L2 Distances (sorted) ===")
        print(f"{'#':<4} {'Face A':<37} {'Face B':<37} {'L2 Dist':>8}")
        print("-" * 90)
        for d in all_distances:
            marker = ""
            if d["l2"] < 0.45:
                marker = " << BELOW 0.45"
            elif d["l2"] < 0.50:
                marker = " << BELOW 0.50"
            elif d["l2"] < 0.55:
                marker = " << BELOW 0.55"
            elif d["l2"] < 0.60:
                marker = " << BELOW 0.60"
            print(f"[{d['i']:>2},{d['j']:>2}] {d['file_a']:<37} {d['file_b']:<37} {d['l2']:>8.4f}{marker}")

        print()
        print("=== Distance Distribution ===")
        bins = [(0, 0.40), (0.40, 0.45), (0.45, 0.50), (0.50, 0.55), (0.55, 0.60), (0.60, 0.65), (0.65, 0.70), (0.70, 0.80), (0.80, 1.0)]
        for lo, hi in bins:
            count = sum(1 for d in all_distances if lo <= d["l2"] < hi)
            bar = "#" * count
            print(f"  {lo:.2f} - {hi:.2f}: {count:>3} {bar}")

        print(f"\n  Min L2: {all_distances[0]['l2']:.4f}")
        print(f"  Max L2: {all_distances[-1]['l2']:.4f}")
        print(f"  Median L2: {all_distances[len(all_distances)//2]['l2']:.4f}")

    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
