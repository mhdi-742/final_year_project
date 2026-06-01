import os
import tempfile
import logging
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Image, Face
from app.schemas import SearchResponse, SearchMatch, ImageListResponse, FaceResponse
from app.services.face_service import FaceService
from app.services.clustering_service import ClusteringService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/by-face", response_model=SearchResponse)
def search_by_face(
    file: UploadFile = File(..., description="Upload a photo containing your face"),
    threshold: Optional[float] = Query(
        default=None,
        description="Distance threshold (0-1). Lower = stricter matching. Default: 0.6",
    ),
    limit: int = Query(default=50, ge=1, le=200, description="Max results to return"),
    db: Session = Depends(get_db),
):
    """
    Upload a photo of a person's face to find all images containing that person.

    The system will:
    1. Detect the face in the uploaded photo
    2. Extract its 128-dim L2-normalized embedding
    3. Search the database for matching faces using cosine distance
    4. Return all images where that person appears, sorted by similarity
    """
    # Save the query image temporarily
    ext = os.path.splitext(file.filename or "query.jpg")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = file.file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # Extract face embedding from the query image
        query_embedding = FaceService.get_face_embedding(tmp_path)

        if query_embedding is None:
            raise HTTPException(
                status_code=400,
                detail="No face detected in the uploaded image. Please upload a clear photo with a visible face.",
            )

        # Search for matching faces in the database
        matches = ClusteringService.find_matching_faces(
            db=db,
            query_embedding=query_embedding,
            threshold=threshold,
            limit=limit,
        )

        # Build response with image and face details
        results = []
        seen_image_ids = set()

        for match in matches:
            # Avoid duplicate images in results (use the closest face match per image)
            if match["image_id"] in seen_image_ids:
                continue
            seen_image_ids.add(match["image_id"])

            # Fetch full image and face objects
            face = db.query(Face).filter(Face.id == match["face_id"]).first()
            image = db.query(Image).filter(Image.id == match["image_id"]).first()

            if face and image:
                distance = match["distance"]
                # Convert cosine distance to similarity percentage (0-100%)
                # Cosine distance 0 = identical (100%), distance 1 = orthogonal (0%)
                similarity = max(0.0, min(100.0, (1.0 - distance) * 100.0))

                results.append(
                    SearchMatch(
                        image=ImageListResponse.model_validate(image),
                        face=FaceResponse.model_validate(face),
                        distance=round(distance, 4),
                        similarity_percent=round(similarity, 2),
                    )
                )

        return SearchResponse(
            query_faces_found=1,
            total_matches=len(results),
            results=results,
        )

    finally:
        # Clean up the temporary file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
