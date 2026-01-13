from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.project import Project, ProjectStatus
from app.models.construction_site import ConstructionSite
from app.models.chat import Chat
from app.models.document import Document, DocumentStatus
from app.schemas.project import ProjectResponse, ProjectStartRequest
from app.schemas.document import DocumentResponse
from app.schemas.base import EmptyResponse

router = APIRouter()


@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    page: int = 0,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Получить список всех проектов строительства
    
    Возвращает список всех доступных проектов с их этапами.
    """
    query = db.query(Project).order_by(Project.created_at.desc())
    if limit is not None:
        query = query.offset(page * limit).limit(limit)
    projects = query.all()
    return projects


@router.get("/requested", response_model=List[ProjectResponse])
async def get_requested_projects(
    page: int = 0,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Получить список проектов в статусе 'requested'
    
    Возвращает проекты, по которым отправлен запрос на строительство.
    """
    query = (
        db.query(Project)
        .filter(Project.status == ProjectStatus.REQUESTED)
        .order_by(Project.created_at.desc())
    )
    if limit is not None:
        query = query.offset(page * limit).limit(limit)
    return query.all()


@router.get("/{id}", response_model=ProjectResponse)
async def get_project(id: UUID, db: Session = Depends(get_db)):
    """
    Получить проект по ID
    
    Возвращает детальную информацию о проекте по его идентификатору.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    return project


@router.post(
    "/{id}/request",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT
)
async def request_construction(id: UUID, db: Session = Depends(get_db)):
    """
    Отправить запрос на строительство проекта
    
    Отправляет запрос на начало строительства проекта.
    Обновляет статус проекта на 'requested'.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    if project.status == ProjectStatus.CONSTRUCTION:
        raise BadRequestError("Construction has already started for this project")
    
    project.status = ProjectStatus.REQUESTED
    db.commit()
    db.refresh(project)
    
    return None


@router.post(
    "/{id}/start",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK
)
async def start_construction(
    id: UUID,
    request: ProjectStartRequest,
    db: Session = Depends(get_db)
):
    """
    Начать строительство проекта.
    
    Создает объект строительства и чат, если их еще нет, обновляет статус проекта.
    Требует, чтобы все документы проекта были подписаны пользователем.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    # Проверяем, что все документы проекта подписаны
    project_documents = db.query(Document).filter(Document.project_id == id).all()
    if project_documents:
        unsigned_documents = [doc for doc in project_documents if doc.signed_at is None]
        if unsigned_documents:
            raise BadRequestError(
                f"All documents must be signed before starting construction. "
                f"Unsigned documents: {', '.join([doc.title for doc in unsigned_documents])}"
            )
    
    # Обновляем адрес проекта из запроса
    project.address = request.address
    
    # Проверяем, существует ли строительная площадка
    construction_site = db.query(ConstructionSite).filter(
        ConstructionSite.project_id == id
    ).first()
    
    if construction_site and construction_site.is_completed:
        raise BadRequestError("Construction is already completed for this project")
    
    if not construction_site:
        construction_site = ConstructionSite(
            project_id=id,
            start_date=datetime.utcnow(),
            progress=0.0,
            all_documents_signed=False,
            is_completed=False,
        )
        db.add(construction_site)
        db.flush()
    
    # Убеждаемся, что есть активный чат
    chat = db.query(Chat).filter(
        Chat.project_id == id,
        Chat.is_active == True  # noqa: E712
    ).first()
    if not chat:
        chat = Chat(
            project_id=id,
            specialist_name="Ваш специалист",
            is_active=True
        )
        db.add(chat)
    
    project.status = ProjectStatus.CONSTRUCTION
    db.commit()
    db.refresh(project)
    
    return project


@router.get(
    "/{id}/documents",
    response_model=List[DocumentResponse],
    status_code=status.HTTP_200_OK
)
async def get_project_documents(
    id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получить список документов проекта
    
    Возвращает все документы, связанные с проектом.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    documents = db.query(Document).filter(Document.project_id == id).all()
    return documents


@router.post(
    "/{id}/documents/{document_id}/sign",
    response_model=EmptyResponse,
    status_code=status.HTTP_200_OK
)
async def sign_project_document(
    id: UUID,
    document_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Подписать документ проекта пользователем
    
    Подписывает документ проекта пользователем, устанавливая signed_at и обновляя статус на 'approved'.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.project_id == id
    ).first()
    if not document:
        raise NotFoundError("Document", str(document_id))
    
    if document.signed_at is not None:
        raise BadRequestError("Document is already signed")
    
    if document.status == DocumentStatus.REJECTED:
        raise BadRequestError("Cannot sign a rejected document")
    
    # Подписываем документ покупателем
    # Только проставляем signed_at, статус остается прежним (админ одобрит позже)
    document.signed_at = datetime.utcnow()
    # Статус не меняем - он останется PENDING или UNDER_REVIEW до одобрения админом
    # approved_at и status = APPROVED будут установлены админом через /documents/{id}/approve
    
    db.commit()
    db.refresh(document)
    
    return EmptyResponse()
