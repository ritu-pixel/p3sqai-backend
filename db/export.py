import io
from typing import List, Dict
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from db.table import FileDB


def _get_file(file_id: str, username: str, db: Session) -> FileDB:
    file = db.query(FileDB).filter_by(id=file_id, uploaded_by=username).first()
    if not file:
        raise ValueError("File not found or access denied.")
    return file

def _extract_summary(file: FileDB) -> str:
    if not file.processed_output or "summary" not in file.processed_output:
        return ""
    return file.processed_output["summary"]

def _extract_clauses(file: FileDB) -> List[Dict]:
    if not file.processed_output or "clauses" not in file.processed_output:
        return []
    return file.processed_output["clauses"]

def get_summary_text(file_id: str, username: str, db: Session) -> str:
    file = _get_file(file_id, username, db)
    return _extract_summary(file)

def get_clause_items(file_id: str, username: str, db: Session) -> List[Dict]:
    file = _get_file(file_id, username, db)
    return _extract_clauses(file)

def export_summary_pdf(file_id: str, username: str, db: Session) -> bytes:
    file = _get_file(file_id, username, db)
    summary = _extract_summary(file)
    clauses = _extract_clauses(file)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("Legal Document Summary", styles["Title"]),
        Spacer(1, 8),
        Paragraph(summary, styles["BodyText"]),
        Spacer(1, 16),
        Paragraph("Key Clauses & Classifications", styles["Heading2"]),
        Spacer(1, 16),
    ]

    data = [["Clause", "Label", "Confidence Score"]]
    for item in clauses:
        data.append([
            item.get("clause", "")[:50] + "...",
            item.get("label", ""),
            f"{item.get('score', 0.0):.2f}"
        ])

    table = Table(data, colWidths=[250, 100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))

    elements.append(table)
    elements.extend(
        (Paragraph("Orignal Text", styles["Heading2"]),
        Paragraph(file.transcribed_text.replace("\n", "<br/>"), styles["BodyText"]))
    )
    doc.build(elements)
    return buffer.getvalue()
