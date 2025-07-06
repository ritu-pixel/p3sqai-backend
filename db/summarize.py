from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel
from typing import Optional

from db.table import FileDB

class TranscriptResponse(BaseModel):
    file_id: UUID
    transcribed_text: str
    processed_output: Optional[dict] = None

    class Config:
        from_attributes = True


def transcribe_and_summarize(file_record: FileDB, db: Session, current_user: str) -> TranscriptResponse:
    # Lazy import heavy function to avoid startup memory spike
    from models.models import classify_clauses

    extracted_text = file_record.transcribed_text
    db.commit()

    try:
        print("Classifying clauses and summarizing text...")
        summary = classify_clauses(extracted_text)

        file_record.processed_output = summary
        file_record.is_summarized = True
        db.commit()

        return TranscriptResponse(
            file_id=file_record.id,
            transcribed_text=extracted_text,
            processed_output=file_record.processed_output
        )

    except Exception as e:
        file_record.processed_output = {"error": str(e)}
        db.commit()

        return TranscriptResponse(
            file_id=file_record.id,
            transcribed_text=extracted_text,
            processed_output=file_record.processed_output
        )
