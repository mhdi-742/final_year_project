import uuid
import os
import shutil
from pathlib import Path
from typing import Tuple

from PIL import Image as PILImage
from fastapi import UploadFile

from app.config import settings


class StorageService:
    """Handles saving, retrieving, and deleting image files on the filesystem."""

    @staticmethod
    def save_upload(file: UploadFile) -> Tuple[str, str, int]:
        """
        Save an uploaded file to the originals directory.

        Returns:
            Tuple of (stored_filename, filepath, file_size)
        """
        # Generate a unique filename to avoid collisions
        ext = Path(file.filename).suffix.lower()
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(settings.ORIGINALS_DIR, stored_filename)

        # Write file to disk
        with open(filepath, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
            file_size = len(content)

        return stored_filename, filepath, file_size

    @staticmethod
    def get_image_dimensions(filepath: str) -> Tuple[int, int]:
        """Get width and height of an image file."""
        with PILImage.open(filepath) as img:
            return img.size  # (width, height)

    @staticmethod
    def save_face_thumbnail(
        image_path: str,
        face_location: Tuple[int, int, int, int],
        padding: int = 20,
    ) -> str:
        """
        Crop a face from the source image and save it as a thumbnail.

        Args:
            image_path: Path to the source image.
            face_location: (top, right, bottom, left) bounding box.
            padding: Extra pixels around the face crop.

        Returns:
            Path to the saved thumbnail.
        """
        top, right, bottom, left = face_location

        with PILImage.open(image_path) as img:
            width, height = img.size

            # Add padding (clamped to image bounds)
            crop_top = max(0, top - padding)
            crop_left = max(0, left - padding)
            crop_bottom = min(height, bottom + padding)
            crop_right = min(width, right + padding)

            face_crop = img.crop((crop_left, crop_top, crop_right, crop_bottom))

            # Save thumbnail
            thumb_filename = f"{uuid.uuid4().hex}.jpg"
            thumb_path = os.path.join(settings.FACES_DIR, thumb_filename)
            face_crop.save(thumb_path, "JPEG", quality=90)

        return thumb_path

    @staticmethod
    def delete_file(filepath: str) -> bool:
        """Delete a file from the filesystem. Returns True if successful."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except OSError:
            pass
        return False

    @staticmethod
    def delete_image_files(image_filepath: str, face_thumbnails: list[str]):
        """Delete the original image and all associated face thumbnails."""
        StorageService.delete_file(image_filepath)
        for thumb_path in face_thumbnails:
            if thumb_path:
                StorageService.delete_file(thumb_path)
