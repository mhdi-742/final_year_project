import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.database import Base


class Image(Base):
    """Represents an uploaded image in the system."""
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    filepath = Column(String(500), nullable=False)
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    face_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed = Column(Boolean, default=False)

    # Relationships
    faces = relationship("Face", back_populates="image", cascade="all, delete-orphan")


class Person(Base):
    """Represents a unique person identified by face clustering."""
    __tablename__ = "persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)  # User-assigned name
    label = Column(String(255), nullable=True)  # Auto-generated label ("Person 1", "Person 2", ...)
    face_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    faces = relationship("Face", back_populates="person")


class Face(Base):
    """Represents a single detected face within an image."""
    __tablename__ = "faces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    person_id = Column(UUID(as_uuid=True), ForeignKey("persons.id", ondelete="SET NULL"), nullable=True)

    # 512-dimensional face embedding from InsightFace ArcFace model
    embedding = Column(Vector(512))

    # Bounding box coordinates (face_recognition format: top, right, bottom, left)
    bbox_top = Column(Integer)
    bbox_right = Column(Integer)
    bbox_bottom = Column(Integer)
    bbox_left = Column(Integer)

    thumbnail_path = Column(String(500))
    confidence = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    image = relationship("Image", back_populates="faces")
    person = relationship("Person", back_populates="faces")
