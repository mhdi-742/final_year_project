import logging
import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

from insightface.app import FaceAnalysis

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class DetectedFace:
    """Represents a single face detected in an image."""
    location: Tuple[int, int, int, int]  # (top, right, bottom, left) — converted from bbox
    embedding: List[float]  # 512-dimensional ArcFace embedding (L2-normalized)


# Initialize InsightFace model once at module level (singleton)
# This avoids reloading the model on every request.
_face_app: Optional[FaceAnalysis] = None


def _get_face_app() -> FaceAnalysis:
    """Lazy-initialize the InsightFace FaceAnalysis model."""
    global _face_app
    if _face_app is None:
        logger.info("Initializing InsightFace ArcFace model (buffalo_l)...")
        _face_app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
        )
        _face_app.prepare(ctx_id=0, det_size=(640, 640))
        logger.info("InsightFace model ready.")
    return _face_app


class FaceService:
    """
    Core face detection and embedding extraction service.
    Uses InsightFace with ArcFace (buffalo_l model pack).

    - Detection: RetinaFace (much more accurate than dlib HOG)
    - Embedding: 512-dimensional ArcFace encoding (L2-normalized)
    - Distance metric: Cosine distance via normed_embedding
    - Accuracy: 99.83% on LFW (vs 99.38% for dlib)
    """

    @staticmethod
    def detect_faces(image_path: str) -> List[DetectedFace]:
        """
        Detect all faces in an image and extract their 512-dim ArcFace embeddings.

        Args:
            image_path: Path to the image file.

        Returns:
            List of DetectedFace objects with location and embedding data.
        """
        app = _get_face_app()

        # Load image with OpenCV (InsightFace expects BGR numpy array)
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return []

        # Detect faces — returns list of Face objects with bbox, embedding, etc.
        faces = app.get(image)

        if not faces:
            logger.info(f"No faces detected in {image_path}")
            return []

        detected_faces = []
        for face in faces:
            # Convert InsightFace bbox (x1, y1, x2, y2) to face_recognition format (top, right, bottom, left)
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
            location = (y1, x2, y2, x1)  # (top, right, bottom, left)

            # Use normed_embedding (L2-normalized) for best cosine similarity results
            embedding = face.normed_embedding.tolist()

            detected_faces.append(
                DetectedFace(
                    location=location,
                    embedding=embedding,
                )
            )

        logger.info(f"Detected {len(detected_faces)} face(s) in {image_path} using InsightFace ArcFace")
        return detected_faces

    @staticmethod
    def get_face_embedding(image_path: str) -> Optional[List[float]]:
        """
        Extract the embedding of the most prominent (largest) face in an image.
        Used for search queries where the user uploads a photo to find matches.

        Returns:
            512-dim L2-normalized embedding list, or None if no face is detected.
        """
        app = _get_face_app()

        image = cv2.imread(image_path)
        if image is None:
            return None

        faces = app.get(image)

        if not faces:
            return None

        # Pick the largest face (by bounding box area)
        largest_face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))

        return largest_face.normed_embedding.tolist()

    @staticmethod
    def compute_distance(embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine distance between two L2-normalized ArcFace embeddings."""
        a = np.array(embedding1)
        b = np.array(embedding2)
        # For L2-normalized vectors: cosine_similarity = dot(a, b)
        cosine_sim = np.dot(a, b)
        return float(1.0 - cosine_sim)

    @staticmethod
    def is_same_person(embedding1: List[float], embedding2: List[float]) -> bool:
        """Check if two embeddings belong to the same person."""
        distance = FaceService.compute_distance(embedding1, embedding2)
        return distance < settings.FACE_MATCH_THRESHOLD
