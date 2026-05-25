import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, init_db
from app.models import Image, Face, Person
from app.schemas import StatsResponse
from app.routers import images, search, persons

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, clean up on shutdown."""
    logger.info("Starting Face Segregation API...")
    init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down Face Segregation API.")


# Create FastAPI app
app = FastAPI(
    title="Face Segregation API",
    description=(
        "Upload images to detect and segregate faces. "
        "Search for a person across all uploaded images by uploading their photo."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files statically (for face thumbnails and originals)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Register routers
app.include_router(images.router, prefix=settings.API_PREFIX)
app.include_router(search.router, prefix=settings.API_PREFIX)
app.include_router(persons.router, prefix=settings.API_PREFIX)


@app.get("/", response_class=FileResponse)
def root():
    """Serve the frontend UI."""
    return FileResponse("frontend/index.html")


@app.get(f"{settings.API_PREFIX}/stats", response_model=StatsResponse, tags=["Stats"])
def get_stats(db: Session = Depends(get_db)):
    """Get system-wide statistics."""
    total_images = db.query(Image).count()
    processed_images = db.query(Image).filter(Image.processed == True).count()
    total_faces = db.query(Face).count()
    total_persons = db.query(Person).count()

    return StatsResponse(
        total_images=total_images,
        total_faces=total_faces,
        total_persons=total_persons,
        processed_images=processed_images,
        unprocessed_images=total_images - processed_images,
    )
