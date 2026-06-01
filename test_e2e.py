"""End-to-end test: detect face, store in DB, verify."""
import traceback

try:
    import os
    import cv2
    from app.services.face_service import FaceService
    from app.database import SessionLocal
    from app.models import Face, Image, Person
    from app.services.clustering_service import ClusteringService
    from app.services.storage_service import StorageService

    # Find a test image
    test_dir = "uploads/originals"
    imgs = [f for f in os.listdir(test_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if not imgs:
        print("No images found in uploads/originals. Please upload one first.")
        exit(1)

    test_path = os.path.join(test_dir, imgs[0])
    print(f"Testing with: {test_path}")

    # Detect faces
    faces = FaceService.detect_faces(test_path)
    print(f"Detected {len(faces)} faces")

    if not faces:
        print("No faces detected. Test complete.")
        exit(0)

    # Test storing in DB
    db = SessionLocal()
    try:
        # Create a test image record
        image = Image(
            original_filename="test.jpg",
            stored_filename=imgs[0],
            filepath=test_path,
            file_size=os.path.getsize(test_path),
        )
        db.add(image)
        db.flush()

        for detected in faces:
            top, right, bottom, left = detected.location
            print(f"  Face bbox: top={top} ({type(top).__name__}), right={right} ({type(right).__name__}), bottom={bottom} ({type(bottom).__name__}), left={left} ({type(left).__name__})")
            print(f"  Embedding length: {len(detected.embedding)}, type: {type(detected.embedding[0]).__name__}")

            # Create face record
            face = Face(
                image_id=image.id,
                embedding=detected.embedding,
                bbox_top=top,
                bbox_right=right,
                bbox_bottom=bottom,
                bbox_left=left,
            )
            db.add(face)
            db.flush()
            print(f"  Face saved to DB: {face.id}")

            # Test clustering
            person = ClusteringService.assign_face_to_person(db, face)
            print(f"  Assigned to person: {person.label}")

        db.rollback()  # Don't actually commit the test data
        print("\nAll OK! Upload should work.")
    finally:
        db.close()

except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()
