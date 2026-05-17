import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Image, Face
from app.schemas import ImageResponse, ImageListResponse
from app.services.storage_service import StorageService
from app.services.face_service import FaceService
from app.services.clustering_service import ClusteringService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/images", tags=["Images"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def _validate_image_file(file: UploadFile):
    """Validate that the uploaded file is an image."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )


@router.post("/upload", response_model=List[ImageResponse])
def upload_images(
    files: List[UploadFile] = File(..., description="One or more image files to upload"),
    db: Session = Depends(get_db),
):
    """
    Upload one or more images. For each image:
    1. Save to filesystem
    2. Detect faces and extract embeddings
    3. Auto-assign faces to person clusters
    4. Save cropped face thumbnails
    """
    results = []

    for file in files:
        _validate_image_file(file)

        # 1. Save file to disk
        stored_filename, filepath, file_size = StorageService.save_upload(file)

        # Get image dimensions
        try:
            width, height = StorageService.get_image_dimensions(filepath)
        except Exception:
            width, height = None, None

        # 2. Create Image record
        image = Image(
            original_filename=file.filename,
            stored_filename=stored_filename,
            filepath=filepath,
            file_size=file_size,
            width=width,
            height=height,
        )
        db.add(image)
        db.flush()  # Get the image ID

        # 3. Detect faces
        try:
            detected_faces = FaceService.detect_faces(filepath)
        except Exception as e:
            logger.error(f"Face detection failed for {file.filename}: {e}")
            detected_faces = []

        # 4. Process each detected face
        for detected in detected_faces:
            # Save face thumbnail
            try:
                thumb_path = StorageService.save_face_thumbnail(
                    filepath, detected.location
                )
            except Exception:
                thumb_path = None

            top, right, bottom, left = detected.location

            # Create Face record
            face = Face(
                image_id=image.id,
                embedding=detected.embedding,
                bbox_top=top,
                bbox_right=right,
                bbox_bottom=bottom,
                bbox_left=left,
                thumbnail_path=thumb_path,
            )
            db.add(face)
            db.flush()

            # Auto-assign to a person cluster
            try:
                ClusteringService.assign_face_to_person(db, face)
            except Exception as e:
                logger.error(f"Clustering failed for face {face.id}: {e}")

        # Update image metadata
        image.face_count = len(detected_faces)
        image.processed = True
        db.flush()

        results.append(image)

    db.commit()

    # Refresh all to load relationships
    for img in results:
        db.refresh(img)

    return results


@router.get("", response_model=List[ImageListResponse])
def list_images(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all uploaded images with pagination."""
    images = (
        db.query(Image)
        .order_by(Image.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return images


@router.get("/{image_id}", response_model=ImageResponse)
def get_image(image_id: UUID, db: Session = Depends(get_db)):
    """Get details of a specific image, including detected faces."""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")
    return image


@router.delete("/{image_id}")
def delete_image(image_id: UUID, db: Session = Depends(get_db)):
    """Delete an image and all its associated face data and files."""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found.")

    # Collect face thumbnails before deletion
    thumb_paths = [f.thumbnail_path for f in image.faces]

    # Update person face counts
    for face in image.faces:
        if face.person_id:
            person = face.person
            if person:
                person.face_count = max(0, person.face_count - 1)

    # Delete from DB (cascades to faces)
    db.delete(image)
    db.commit()

    # Delete files from filesystem
    StorageService.delete_image_files(image.filepath, thumb_paths)

    return {"message": "Image deleted successfully.", "id": str(image_id)}
