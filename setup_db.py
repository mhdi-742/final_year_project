"""
Database initialization script.

Run this once to set up the database:
    python setup_db.py

Requires:
    - PostgreSQL running with a database named 'face_segregation'
    - pgvector extension available in PostgreSQL
"""

from app.database import init_db


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Done! The database is ready.")
    print("Start the server with: uvicorn app.main:app --reload")
