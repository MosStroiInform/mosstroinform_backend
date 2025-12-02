from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.project import Project
from app.models.construction_site import ConstructionSite
from app.models.completion import FinalDocument, FinalDocumentStatus
from app.schemas.completion import (
    CompletionStatusResponse,
    FinalDocumentResponse,
    FinalDocumentRejectRequest,
    EmptyResponse
)

router = APIRouter()


@router.get("/{project_id}/completion-status", response_model=CompletionStatusResponse)
async def get_completion_status(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получить статус завершения строительства проекта
    
    Возвращает статус завершения строительства проекта, включая прогресс
    и список финальных документов.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundError("Project", str(project_id))
    
    # Получаем строительную площадку для прогресса
    construction_site = db.query(ConstructionSite).filter(
        ConstructionSite.project_id == project_id
    ).first()
    
    progress = construction_site.progress if construction_site else 0.0
    
    # Получаем финальные документы
    final_documents = db.query(FinalDocument).filter(
        FinalDocument.project_id == project_id
    ).all()
    
    # Определяем статус завершения
    # Считаем завершенным, если прогресс = 1.0 и все документы подписаны
    is_completed = False
    completion_date = None
    
    if progress >= 1.0:
        all_signed = all(
            doc.status == FinalDocumentStatus.SIGNED
            for doc in final_documents
            if doc.status != FinalDocumentStatus.REJECTED
        )
        if all_signed and final_documents:
            is_completed = True
            # Берем дату подписания последнего документа
            signed_docs = [
                doc for doc in final_documents
                if doc.signed_at is not None
            ]
            if signed_docs:
                completion_date = max(doc.signed_at for doc in signed_docs)
    
    response_data = {
        "project_id": project_id,
        "is_completed": is_completed,
        "completion_date": completion_date,
        "progress": progress,
        "documents": final_documents,
    }
    
    return CompletionStatusResponse(**response_data)


@router.get("/{project_id}/final-documents", response_model=List[FinalDocumentResponse])
async def get_final_documents(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получить список финальных документов проекта
    
    Возвращает список всех финальных документов для указанного проекта.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundError("Project", str(project_id))
    
    final_documents = db.query(FinalDocument).filter(
        FinalDocument.project_id == project_id
    ).all()
    
    return final_documents


@router.get("/{project_id}/final-documents/{document_id}", response_model=FinalDocumentResponse)
async def get_final_document(
    project_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получить финальный документ по ID
    
    Возвращает детальную информацию о финальном документе проекта.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundError("Project", str(project_id))
    
    document = db.query(FinalDocument).filter(
        FinalDocument.id == document_id,
        FinalDocument.project_id == project_id
    ).first()
    
    if not document:
        raise NotFoundError("Final document", str(document_id))
    
    return document


@router.post(
    "/{project_id}/final-documents/{document_id}/sign",
    response_model=EmptyResponse,
    status_code=status.HTTP_200_OK
)
async def sign_final_document(
    project_id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Подписать финальный документ
    
    Подписывает финальный документ, изменяя его статус на 'signed'.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundError("Project", str(project_id))
    
    document = db.query(FinalDocument).filter(
        FinalDocument.id == document_id,
        FinalDocument.project_id == project_id
    ).first()
    
    if not document:
        raise NotFoundError("Final document", str(document_id))
    
    if document.status == FinalDocumentStatus.SIGNED:
        raise BadRequestError("Document is already signed")
    
    if document.status == FinalDocumentStatus.REJECTED:
        raise BadRequestError("Cannot sign a rejected document")
    
    document.status = FinalDocumentStatus.SIGNED
    document.signed_at = datetime.utcnow()
    document.rejection_reason = None
    
    db.commit()
    db.refresh(document)
    
    return EmptyResponse()


@router.post(
    "/{project_id}/final-documents/{document_id}/reject",
    response_model=EmptyResponse,
    status_code=status.HTTP_200_OK
)
async def reject_final_document(
    project_id: UUID,
    document_id: UUID,
    request: FinalDocumentRejectRequest,
    db: Session = Depends(get_db)
):
    """
    Отклонить финальный документ
    
    Отклоняет финальный документ с указанием причины, изменяя его статус на 'rejected'.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundError("Project", str(project_id))
    
    document = db.query(FinalDocument).filter(
        FinalDocument.id == document_id,
        FinalDocument.project_id == project_id
    ).first()
    
    if not document:
        raise NotFoundError("Final document", str(document_id))
    
    if document.status == FinalDocumentStatus.SIGNED:
        raise BadRequestError("Cannot reject a signed document")
    
    if document.status == FinalDocumentStatus.REJECTED:
        raise BadRequestError("Document is already rejected")
    
    document.status = FinalDocumentStatus.REJECTED
    document.rejection_reason = request.reason
    document.signed_at = None
    document.signature_url = None
    
    db.commit()
    db.refresh(document)
    
    return EmptyResponse()
