from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Person, Face, Image
from app.schemas import PersonResponse, PersonDetailResponse, PersonUpdate, ImageListResponse

router = APIRouter(prefix="/persons", tags=["Persons"])


@router.get("", response_model=List[PersonResponse])
def list_persons(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all identified persons/clusters with their first face thumbnail."""
    persons = (
        db.query(Person)
        .order_by(Person.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Attach thumbnail_path from the first face of each person
    result = []
    for person in persons:
        first_face = (
            db.query(Face)
            .filter(Face.person_id == person.id, Face.thumbnail_path.isnot(None))
            .order_by(Face.created_at.asc())
            .first()
        )
        person_dict = {
            "id": person.id,
            "name": person.name,
            "label": person.label,
            "face_count": person.face_count,
            "thumbnail_path": first_face.thumbnail_path if first_face else None,
            "created_at": person.created_at,
            "updated_at": person.updated_at,
        }
        result.append(person_dict)

    return result


@router.get("/{person_id}", response_model=PersonDetailResponse)
def get_person(person_id: UUID, db: Session = Depends(get_db)):
    """Get details of a person including all their detected faces."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found.")
    return person


@router.get("/{person_id}/images", response_model=List[ImageListResponse])
def get_person_images(person_id: UUID, db: Session = Depends(get_db)):
    """Get all images where a specific person appears."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found.")

    # Get all images containing this person's faces
    images = (
        db.query(Image)
        .join(Face, Face.image_id == Image.id)
        .filter(Face.person_id == person_id)
        .distinct()
        .order_by(Image.uploaded_at.desc())
        .all()
    )
    return images


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(person_id: UUID, data: PersonUpdate, db: Session = Depends(get_db)):
    """Update a person's name (label them)."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found.")

    person.name = data.name
    db.commit()
    db.refresh(person)
    return person


@router.delete("/{person_id}")
def delete_person(person_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a person cluster. Faces are unlinked (not deleted),
    so they can be re-clustered later.
    """
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found.")

    # Unlink all faces from this person
    db.query(Face).filter(Face.person_id == person_id).update(
        {"person_id": None}, synchronize_session="fetch"
    )

    db.delete(person)
    db.commit()

    return {"message": "Person deleted successfully.", "id": str(person_id)}
