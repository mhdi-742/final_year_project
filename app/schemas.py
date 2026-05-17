from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID


# ─── Face Schemas ───────────────────────────────────────────────────────────────

class FaceResponse(BaseModel):
    """Response schema for a detected face."""
    id: UUID
    image_id: UUID
    person_id: Optional[UUID] = None
    bbox_top: int
    bbox_right: int
    bbox_bottom: int
    bbox_left: int
    thumbnail_path: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Person Schemas ─────────────────────────────────────────────────────────────

class PersonUpdate(BaseModel):
    """Schema for updating a person's name."""
    name: str


class PersonResponse(BaseModel):
    """Response schema for a person/cluster."""
    id: UUID
    name: Optional[str] = None
    label: Optional[str] = None
    face_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PersonDetailResponse(PersonResponse):
    """Detailed person response including all their faces."""
    faces: List[FaceResponse] = []

    model_config = {"from_attributes": True}


# ─── Image Schemas ──────────────────────────────────────────────────────────────

class ImageResponse(BaseModel):
    """Full image response with detected faces."""
    id: UUID
    original_filename: str
    stored_filename: str
    filepath: str
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    face_count: int
    uploaded_at: datetime
    processed: bool
    faces: List[FaceResponse] = []

    model_config = {"from_attributes": True}


class ImageListResponse(BaseModel):
    """Lightweight image response for listing."""
    id: UUID
    original_filename: str
    stored_filename: str
    file_size: Optional[int] = None
    face_count: int
    uploaded_at: datetime
    processed: bool

    model_config = {"from_attributes": True}


# ─── Search Schemas ─────────────────────────────────────────────────────────────

class SearchMatch(BaseModel):
    """A single search result: matched face + source image."""
    image: ImageListResponse
    face: FaceResponse
    distance: float
    similarity_percent: float


class SearchResponse(BaseModel):
    """Response for a face search query."""
    query_faces_found: int
    total_matches: int
    results: List[SearchMatch]


# ─── Stats Schema ──────────────────────────────────────────────────────────────

class StatsResponse(BaseModel):
    """System-wide statistics."""
    total_images: int
    total_faces: int
    total_persons: int
    processed_images: int
    unprocessed_images: int
