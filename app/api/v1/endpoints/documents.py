from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentResponse, DocumentRejectRequest, EmptyResponse

router = APIRouter()


@router.get("", response_model=List[DocumentResponse])
async def get_documents(db: Session = Depends(get_db)):
    """
    Получить список всех документов
    
    Возвращает список всех документов, требующих согласования.
    """
    documents = db.query(Document).all()
    return documents


@router.get("/{id}", response_model=DocumentResponse)
async def get_document(id: UUID, db: Session = Depends(get_db)):
    """
    Получить документ по ID
    
    Возвращает детальную информацию о документе по его идентификатору.
    """
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise NotFoundError("Document", str(id))
    return document


@router.post("/{id}/approve", response_model=EmptyResponse, status_code=status.HTTP_200_OK)
async def approve_document(id: UUID, db: Session = Depends(get_db)):
    """
    Одобрить документ
    
    Одобряет документ, изменяя его статус на 'approved'.
    """
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise NotFoundError("Document", str(id))
    
    if document.status == DocumentStatus.APPROVED:
        raise BadRequestError("Document is already approved")
    
    if document.status == DocumentStatus.REJECTED:
        raise BadRequestError("Cannot approve a rejected document")
    
    document.status = DocumentStatus.APPROVED
    document.approved_at = datetime.utcnow()
    document.rejection_reason = None
    
    db.commit()
    db.refresh(document)
    
    return EmptyResponse()


@router.post("/{id}/reject", response_model=EmptyResponse, status_code=status.HTTP_200_OK)
async def reject_document(
    id: UUID,
    request: DocumentRejectRequest,
    db: Session = Depends(get_db)
):
    """
    Отклонить документ
    
    Отклоняет документ с указанием причины, изменяя его статус на 'rejected'.
    """
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise NotFoundError("Document", str(id))
    
    if document.status == DocumentStatus.APPROVED:
        raise BadRequestError("Cannot reject an approved document")
    
    if document.status == DocumentStatus.REJECTED:
        raise BadRequestError("Document is already rejected")
    
    document.status = DocumentStatus.REJECTED
    document.rejection_reason = request.reason
    document.approved_at = None
    
    db.commit()
    db.refresh(document)
    
    return EmptyResponse()
