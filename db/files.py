import os
import uuid
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from db.table import UserDB, FileDB
from models.models import extract_text_from_pdf, ocr_pdf, is_scanned_pdf, detect_language

class FileResponse(BaseModel):
    id: UUID
    filename: str
    content_type: str
    uploaded_at: datetime
    uploaded_by: str
    is_summarized: bool = False
    original_language: Optional[str] = None
    transcribed_text: Optional[str] = None
    processed_output: Optional[dict] = None
    class Config:
        from_attributes = True

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def save(file, username: str, db: Session) -> FileDB:
    """Temporarily store file, extract text, save text + metadata to DB, delete file."""

    file_id = str(uuid.uuid4())
    temp_path = os.path.join(TEMP_DIR, f"{file_id}.pdf")

    with open(temp_path, "wb") as temp_file:
        temp_file.write(file.file.read())

    try:
        if is_scanned_pdf(temp_path):
            extracted_text = ocr_pdf(temp_path)
        else:
            extracted_text = extract_text_from_pdf(temp_path)

        lang = detect_language(extracted_text)

        record = FileDB(
            id=file_id,
            filename=file.filename,
            content_type=file.content_type,
            uploaded_by=username,
            original_language=lang,
            transcribed_text=extracted_text,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)



def get(file_id: str, username: str, db: Session) -> Optional[FileDB]:
    """Fetch a specific file by ID, belonging to the given user."""
    return (
        db.query(FileDB)
        .join(FileDB.uploader)
        .filter(FileDB.id == file_id, UserDB.username == username)
        .first()
    )


def get_all(username: str, db: Session) -> List[FileDB]:
    """List all uploaded files for a user, optionally filtered by status."""
    query = (
        db.query(FileDB)
        .join(FileDB.uploader)
        .filter(UserDB.username == username)
    )
    return query.all()


def remove(file_id: str, username: str, db: Session) -> bool:
    """Delete file from disk and remove its DB record."""
    file_record = (
        db.query(FileDB)
        .filter_by(id=file_id, uploaded_by=username)
        .first()
    )
    if not file_record:
        return False

    try:
        if os.path.exists(file_record.storage_path):
            os.remove(file_record.storage_path)
    except Exception:
        pass

    db.delete(file_record)
    db.commit()
    return True
