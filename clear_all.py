import os
import shutil
from pathlib import Path
from sqlalchemy import text
from app.database import SessionLocal, engine
from app.config import settings
from app.models import Face, Image, Person

def clear_database_and_files():
    print("Connecting to the database...")
    db = SessionLocal()
    try:
        # 1. Delete database records in correct dependency order (faces -> images, persons)
        print("Deleting records from database...")
        db.execute(text("DELETE FROM faces;"))
        db.execute(text("DELETE FROM images;"))
        db.execute(text("DELETE FROM persons;"))
        db.commit()
        print("Database records deleted successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error deleting database records: {e}")
        return
    finally:
        db.close()

    # 2. Delete files from filesystem
    print("\nCleaning up filesystem uploads...")
    
    # Clean originals directory
    originals_dir = Path(settings.ORIGINALS_DIR)
    if originals_dir.exists():
        files_deleted = 0
        for file_path in originals_dir.iterdir():
            if file_path.is_file():
                try:
                    file_path.unlink()
                    files_deleted += 1
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
        print(f"Deleted {files_deleted} file(s) from {originals_dir}")

    # Clean faces directory
    faces_dir = Path(settings.FACES_DIR)
    if faces_dir.exists():
        files_deleted = 0
        for file_path in faces_dir.iterdir():
            if file_path.is_file():
                try:
                    file_path.unlink()
                    files_deleted += 1
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
        print(f"Deleted {files_deleted} file(s) from {faces_dir}")

    print("\nSystem cleared successfully!")

if __name__ == "__main__":
    clear_database_and_files()
