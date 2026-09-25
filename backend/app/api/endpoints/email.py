from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import StructuredStateModel
from app.models.pydantic_models import EmailSendRequest
from app.services.pdf_exporter import PDFExporter
from app.services.email_service import EmailService

router = APIRouter(prefix="/sessions", tags=["Email"])

@router.post("/{session_id}/email")
def send_email(session_id: str, body: EmailSendRequest, db: Session = Depends(get_db)):
    state_record = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
    if not state_record:
        raise HTTPException(status_code=404, detail="Structured state not found")

    data = state_record.state_json.get("data", {})
    pdf_bytes = PDFExporter.generate_pdf_bytes(data)

    success, message = EmailService.send_document_email(
        recipient_email=body.email,
        pdf_bytes=pdf_bytes,
        filename=f"Personal_Wishes_Document_{session_id[:8]}.pdf"
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"status": "success", "message": message}
