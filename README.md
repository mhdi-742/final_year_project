# Face Segregation API

A backend system that automatically detects, segregates, and clusters faces from uploaded images. Upload photos → faces are detected and grouped by person → search for any person by uploading their photo.

## Features

- **Image Upload & Face Detection**: Upload images; the system automatically detects all faces and extracts 128-dimensional embeddings.
- **Auto-Clustering**: Detected faces are automatically grouped into person clusters using L2 distance matching.
- **Face Search**: Upload a photo of someone to find all images they appear in.
- **Person Management**: View, rename, and manage identified person clusters.
- **Face Thumbnails**: Automatically crops and stores face thumbnails for quick preview.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL + pgvector |
| Face Recognition | `face_recognition` (dlib) |
| ORM | SQLAlchemy 2.0 |
| Image Processing | Pillow |

## Prerequisites

1. **Python 3.10+**
2. **PostgreSQL 14+** with the `pgvector` extension
3. **CMake** and **C++ Build Tools** (required for dlib)

### Installing pgvector on PostgreSQL

```sql
-- Connect to PostgreSQL and run:
CREATE EXTENSION IF NOT EXISTS vector;
```

If pgvector is not available, install it:
- **Windows**: Download from [pgvector releases](https://github.com/pgvector/pgvector/releases) or use `vcpkg`
- **macOS**: `brew install pgvector`
- **Linux**: `sudo apt install postgresql-16-pgvector`

### Installing dlib dependencies (Windows)

```bash
# Install Visual Studio Build Tools with C++ workload, then:
pip install cmake
pip install dlib
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the PostgreSQL database

```sql
CREATE DATABASE face_segregation;
```

### 4. Configure environment

Copy `.env.example` to `.env` and update the database URL:

```bash
copy .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/face_segregation
```

### 5. Initialize the database

```bash
python setup_db.py
```

### 6. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/images/upload` | Upload image(s) and detect faces |
| `GET` | `/api/images` | List all uploaded images |
| `GET` | `/api/images/{id}` | Get image details + faces |
| `DELETE` | `/api/images/{id}` | Delete an image |
| `POST` | `/api/search/by-face` | Search for a person by face photo |
| `GET` | `/api/persons` | List all person clusters |
| `GET` | `/api/persons/{id}` | Get person details |
| `GET` | `/api/persons/{id}/images` | Get all images of a person |
| `PUT` | `/api/persons/{id}` | Rename a person |
| `DELETE` | `/api/persons/{id}` | Delete a person cluster |
| `GET` | `/api/stats` | System statistics |

## Usage Example

### 1. Upload images

```bash
curl -X POST "http://localhost:8000/api/images/upload" \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.jpg"
```

### 2. Search by face

```bash
curl -X POST "http://localhost:8000/api/search/by-face" \
  -F "file=@my_selfie.jpg"
```

### 3. View detected persons

```bash
curl "http://localhost:8000/api/persons"
```

## Project Structure

```
final_year_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + startup
│   ├── config.py             # Settings (from .env)
│   ├── database.py           # DB engine & session
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── routers/
│   │   ├── images.py         # Image CRUD endpoints
│   │   ├── search.py         # Face search endpoint
│   │   └── persons.py        # Person management
│   └── services/
│       ├── face_service.py       # Face detection & embeddings
│       ├── clustering_service.py # Auto-clustering logic
│       └── storage_service.py    # File storage
├── uploads/                  # Image storage (auto-created)
├── requirements.txt
├── setup_db.py               # DB init script
├── .env                      # Environment config
└── README.md
```
