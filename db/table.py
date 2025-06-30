from sqlalchemy import Column, String, DateTime, Enum, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum as pyEnum
from datetime import datetime
import uuid

from db.database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    files = relationship("FileDB", back_populates="uploader", cascade="all, delete-orphan")

class FileDB(Base):
    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    uploaded_by = Column(String, ForeignKey("users.username", ondelete="CASCADE"), nullable=False)
    uploader = relationship("UserDB", back_populates="files")

    is_summarized = Column(Boolean, default=False)
    original_language = Column(String, nullable=True)
    transcribed_text = Column(String, nullable=False)
    processed_output = Column(JSON, nullable=True)
