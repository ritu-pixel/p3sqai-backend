from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from db.database import get_db
from db.files import (
    save,
    remove,
    get,
    get_all,
    FileResponse
)
from auth.dependencies import get_current_user

router = APIRouter(prefix="/file", tags=["File Management"])


@router.post("/upload", response_model=FileResponse)
async def upload_document(
    document: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    if document.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    saved_file = save(document, current_user.username, db)
    return saved_file


@router.get("/", response_model=List[FileResponse])
def list_user_documents(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    return get_all(current_user.username, db)


@router.get("/{file_id}", response_model=FileResponse)
def get_document(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    document = get(file_id, current_user.username, db)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found or access denied")
    return document


@router.delete("/{file_id}", status_code=status.HTTP_200_OK)
def delete_document(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    deleted = remove(file_id, current_user.username, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found or access denied")
    return {"message": f"Document {file_id} deleted successfully."}

