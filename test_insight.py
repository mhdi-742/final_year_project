"""Quick test: upload a file through the face pipeline to find the error."""
import sys
import traceback

try:
    print("1. Importing FaceService...")
    from app.services.face_service import FaceService
    print("   OK")

    print("2. Testing with a sample image...")
    import os
    # Find an image to test with
    test_dir = "uploads/originals"
    if os.path.exists(test_dir):
        imgs = [f for f in os.listdir(test_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        if imgs:
            test_path = os.path.join(test_dir, imgs[0])
            print(f"   Found: {test_path}")
        else:
            print("   No images in uploads. Using a test with cv2...")
            test_path = None
    else:
        test_path = None

    if test_path is None:
        # Create a dummy test image
        import cv2
        import numpy as np
        test_path = "test_insight.jpg"
        img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.imwrite(test_path, img)
        print(f"   Created dummy image: {test_path}")

    print("3. Running face detection...")
    faces = FaceService.detect_faces(test_path)
    print(f"   Detected {len(faces)} faces")

    for i, face in enumerate(faces):
        print(f"   Face {i}: location={face.location}, embedding_len={len(face.embedding)}")

    print("\n4. Testing get_face_embedding...")
    emb = FaceService.get_face_embedding(test_path)
    print(f"   Embedding: {'None (no face)' if emb is None else f'{len(emb)} dimensions'}")

    print("\nAll OK!")

except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()
