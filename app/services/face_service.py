import numpy as np
import face_recognition
from typing import List, Tuple, Optional
from dataclasses import dataclass

from app.config import settings


@dataclass
class DetectedFace:
    """Represents a single face detected in an image."""
    location: Tuple[int, int, int, int]  # (top, right, bottom, left)
    embedding: List[float]  # 128-dimensional face encoding


class FaceService:
    """
    Core face detection and embedding extraction service.
    Uses the `face_recognition` library (dlib under the hood).

    - Detection model: "hog" (fast, CPU) or "cnn" (accurate, GPU-recommended)
    - Embedding: 128-dimensional face encoding
    - Distance metric: Euclidean (L2), threshold ~0.6
    """

    @staticmethod
    def detect_faces(image_path: str) -> List[DetectedFace]:
        """
        Detect all faces in an image and extract their 128-dim embeddings.

        Args:
            image_path: Path to the image file.

        Returns:
            List of DetectedFace objects with location and embedding data.
        """
        # Load image
        image = face_recognition.load_image_file(image_path)

        # Detect face locations
        face_locations = face_recognition.face_locations(
            image, model=settings.FACE_DETECTION_MODEL
        )

        if not face_locations:
            return []

        # Extract 128-dim embeddings for each detected face
        face_encodings = face_recognition.face_encodings(image, face_locations)

        detected_faces = []
        for location, encoding in zip(face_locations, face_encodings):
            detected_faces.append(
                DetectedFace(
                    location=location,
                    embedding=encoding.tolist(),
                )
            )

        return detected_faces

    @staticmethod
    def get_face_embedding(image_path: str) -> Optional[List[float]]:
        """
        Extract the embedding of the most prominent face in an image.
        Used for search queries where the user uploads a photo of themselves.

        Returns:
            128-dim embedding list, or None if no face is detected.
        """
        image = face_recognition.load_image_file(image_path)

        face_locations = face_recognition.face_locations(
            image, model=settings.FACE_DETECTION_MODEL
        )

        if not face_locations:
            return None

        # Get encoding for the first (largest / most prominent) face
        encodings = face_recognition.face_encodings(image, [face_locations[0]])

        if not encodings:
            return None

        return encodings[0].tolist()

    @staticmethod
    def compute_distance(embedding1: List[float], embedding2: List[float]) -> float:
        """Compute Euclidean distance between two face embeddings."""
        return float(np.linalg.norm(np.array(embedding1) - np.array(embedding2)))

    @staticmethod
    def is_same_person(embedding1: List[float], embedding2: List[float]) -> bool:
        """Check if two embeddings belong to the same person."""
        distance = FaceService.compute_distance(embedding1, embedding2)
        return distance < settings.FACE_MATCH_THRESHOLD
