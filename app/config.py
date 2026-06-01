import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/face_segregation"

    # Storage paths
    UPLOAD_DIR: str = "uploads"
    ORIGINALS_DIR: str = "uploads/originals"
    FACES_DIR: str = "uploads/faces"

    # Face Recognition settings (InsightFace ArcFace)
    # Cosine distance threshold: normed embeddings produce distances 0 (identical) to 2 (opposite)
    # ArcFace typical same-person distance: 0.0 - 0.4
    # ArcFace typical different-person distance: 0.5+
    # The gap is much wider than dlib, making thresholding reliable.
    FACE_MATCH_THRESHOLD: float = 0.45  # Cosine distance threshold for ArcFace
    FACE_DETECTION_MODEL: str = "buffalo_l"  # InsightFace model pack

    # API
    API_PREFIX: str = "/api"

    model_config = {"env_file": ".env", "extra": "ignore"}

    def ensure_directories(self):
        """Create storage directories if they don't exist."""
        for dir_path in [self.UPLOAD_DIR, self.ORIGINALS_DIR, self.FACES_DIR]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
