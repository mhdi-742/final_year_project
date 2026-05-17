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

    # Face Recognition settings
    FACE_MATCH_THRESHOLD: float = 0.6  # L2 distance threshold (lower = stricter)
    FACE_DETECTION_MODEL: str = "hog"  # "hog" (faster, CPU) or "cnn" (more accurate, GPU)

    # API
    API_PREFIX: str = "/api"

    model_config = {"env_file": ".env", "extra": "ignore"}

    def ensure_directories(self):
        """Create storage directories if they don't exist."""
        for dir_path in [self.UPLOAD_DIR, self.ORIGINALS_DIR, self.FACES_DIR]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
