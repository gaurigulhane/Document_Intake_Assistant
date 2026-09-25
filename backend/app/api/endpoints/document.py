from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.database_models import StructuredStateModel
from app.models.pydantic_models import DocumentResponse
from app.services.document_generator import DocumentGenerator
from app.services.pdf_exporter import PDFExporter

router = APIRouter(prefix="/sessions", tags=["Document Generation"])

@router.post("/{session_id}/document", response_model=DocumentResponse)
def generate_document(session_id: str, db: Session = Depends(get_db)):
    state_record = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
    if not state_record:
        raise HTTPException(status_code=404, detail="Structured state not found")

    data = state_record.state_json.get("data", {})
    doc_text = DocumentGenerator.generate_draft(data)

    return DocumentResponse(
        session_id=session_id,
        disclaimer="FICTIONAL DOCUMENT — NOT LEGAL ADVICE",
        document_text=doc_text,
        generated_at=datetime.utcnow().isoformat()
    )

@router.get("/{session_id}/document/pdf")
def download_pdf(session_id: str, db: Session = Depends(get_db)):
    state_record = db.query(StructuredStateModel).filter(StructuredStateModel.session_id == session_id).first()
    if not state_record:
        raise HTTPException(status_code=404, detail="Structured state not found")

    data = state_record.state_json.get("data", {})
    pdf_bytes = PDFExporter.generate_pdf_bytes(data)

    headers = {
        'Content-Disposition': f'attachment; filename="Personal_Wishes_Document_{session_id[:8]}.pdf"'
    }

    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
