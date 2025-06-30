from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from db.database import get_db
from auth.dependencies import get_current_user
from db.export import export_summary_pdf

router = APIRouter(
    prefix="/export",
    tags=["Export"],
)

@router.get("/pdf/{file_id}")
def download_pdf(
    file_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    pdf_bytes = export_summary_pdf(file_id, current_user.username, db)
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=summary_{file_id}.pdf"
    })