from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.project import Project, ProjectStatus, ProjectStage, StageStatus
from app.models.document import Document, DocumentStatus
from app.models.construction_site import ConstructionSite
# ConstructionObject - это схема ответа, а не модель
from app.models.chat import Chat, Message
from app.schemas.project import ProjectResponse, ProjectStartRequest
from app.schemas.base import BaseSchema, EmptyResponse
from pydantic import BaseModel, Field

router = APIRouter()


# ==================== СХЕМЫ ====================

class ProjectCreateRequest(BaseModel):
    """Схема создания проекта"""
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    description: str = ""
    area: float = Field(..., gt=0)
    floors: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    bedrooms: int = 0
    bathrooms: int = 0
    image_url: Optional[str] = None
    stages: List[str] = []  # Список названий этапов


class ProjectUpdateRequest(BaseModel):
    """Схема обновления проекта"""
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    area: Optional[float] = None
    floors: Optional[int] = None
    price: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    image_url: Optional[str] = None
    status: Optional[str] = None  # "available" | "requested" | "construction"


class StageCreateRequest(BaseModel):
    """Схема создания этапа"""
    name: str = Field(..., min_length=1)


class StageUpdateRequest(BaseModel):
    """Схема обновления этапа"""
    name: Optional[str] = None
    status: Optional[str] = None  # "pending" | "in_progress" | "completed"


class RequestRejectRequest(BaseModel):
    """Схема отклонения запроса"""
    reason: str = Field(..., min_length=1)


class ProgressUpdateRequest(BaseModel):
    """Схема обновления прогресса"""
    progress: float = Field(..., ge=0.0, le=1.0)


class StageStatusUpdateRequest(BaseModel):
    """Схема обновления статуса этапа объекта"""
    status: str = Field(..., pattern="^(pending|in_progress|completed)$")


class StatisticsResponse(BaseSchema):
    """Схема статистики"""
    totalProjects: int
    availableProjects: int
    requestedProjects: int
    inProgressProjects: int
    totalDocuments: int
    pendingDocuments: int
    approvedDocuments: int
    rejectedDocuments: int
    totalRevenue: float
    averageProjectPrice: float


class BatchApproveRequest(BaseModel):
    """Схема массового одобрения"""
    ids: List[UUID] = Field(..., min_items=1)


class BatchRejectRequest(BaseModel):
    """Схема массового отклонения"""
    ids: List[UUID] = Field(..., min_items=1)
    reason: str = Field(..., min_length=1)


class NotificationResponse(BaseSchema):
    """Схема уведомления"""
    id: UUID
    type: str  # "new_request" | "new_document" | "new_message" | "camera_offline"
    title: str
    message: str
    projectId: Optional[UUID] = None
    documentId: Optional[UUID] = None
    chatId: Optional[UUID] = None
    isRead: bool
    createdAt: datetime


# ==================== УПРАВЛЕНИЕ ПРОЕКТАМИ (CRUD) ====================

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: ProjectCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Создать новый проект
    
    Создает новый проект с указанными параметрами и этапами.
    """
    project = Project(
        name=request.name,
        address=request.address,
        description=request.description,
        area=request.area,
        floors=request.floors,
        price=request.price,
        bedrooms=request.bedrooms,
        bathrooms=request.bathrooms,
        image_url=request.image_url,
        status=ProjectStatus.AVAILABLE
    )
    db.add(project)
    db.flush()
    
    # Создаем этапы
    for stage_name in request.stages:
        stage = ProjectStage(
            project_id=project.id,
            name=stage_name,
            status=StageStatus.PENDING
        )
        db.add(stage)
    
    db.commit()
    db.refresh(project)
    # Явно сериализуем через Pydantic для правильного формата
    project_response = ProjectResponse.model_validate(project)
    return project_response


@router.put("/{id}", response_model=ProjectResponse)
async def update_project(
    id: UUID,
    request: ProjectUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Обновить проект
    
    Обновляет параметры проекта. Можно обновить только указанные поля.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    if request.name is not None:
        project.name = request.name
    if request.address is not None:
        project.address = request.address
    if request.description is not None:
        project.description = request.description
    if request.area is not None:
        project.area = request.area
    if request.floors is not None:
        project.floors = request.floors
    if request.price is not None:
        project.price = request.price
    if request.bedrooms is not None:
        project.bedrooms = request.bedrooms
    if request.bathrooms is not None:
        project.bathrooms = request.bathrooms
    if request.image_url is not None:
        project.image_url = request.image_url
    if request.status is not None:
        try:
            project.status = ProjectStatus(request.status)
        except ValueError:
            raise BadRequestError(f"Invalid status: {request.status}")
    
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    id: UUID,
    db: Session = Depends(get_db)
):
    """
    Удалить проект
    
    Удаляет проект и все связанные данные (этапы, документы и т.д.).
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    db.delete(project)
    db.commit()
    return None


# ==================== УПРАВЛЕНИЕ ЭТАПАМИ ПРОЕКТА ====================

@router.post("/{id}/stages", response_model=ProjectStageResponse, status_code=status.HTTP_201_CREATED)
async def create_stage(
    id: UUID,
    request: StageCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Добавить этап к проекту
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    stage = ProjectStage(
        project_id=id,
        name=request.name,
        status=StageStatus.PENDING
    )
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage


@router.put("/{id}/stages/{stage_id}", response_model=ProjectStageResponse)
async def update_stage(
    id: UUID,
    stage_id: UUID,
    request: StageUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Обновить этап проекта
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    stage = db.query(ProjectStage).filter(
        ProjectStage.id == stage_id,
        ProjectStage.project_id == id
    ).first()
    if not stage:
        raise NotFoundError("Stage", str(stage_id))
    
    if request.name is not None:
        stage.name = request.name
    if request.status is not None:
        try:
            stage.status = StageStatus(request.status)
        except ValueError:
            raise BadRequestError(f"Invalid status: {request.status}")
    
    stage.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(stage)
    return stage


@router.delete("/{id}/stages/{stage_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_stage(
    id: UUID,
    stage_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Удалить этап проекта
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    stage = db.query(ProjectStage).filter(
        ProjectStage.id == stage_id,
        ProjectStage.project_id == id
    ).first()
    if not stage:
        raise NotFoundError("Stage", str(stage_id))
    
    db.delete(stage)
    db.commit()
    return None


# ==================== УПРАВЛЕНИЕ ЗАПРОСАМИ ====================

@router.post("/{id}/approve-request", response_model=ProjectResponse)
async def approve_request(
    id: UUID,
    request: ProjectStartRequest,
    db: Session = Depends(get_db)
):
    """
    Одобрить запрос на строительство
    
    Одобряет запрос и начинает строительство (аналогично /start, но для админа).
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    if project.status != ProjectStatus.REQUESTED:
        raise BadRequestError("Project is not in REQUESTED status")
    
    # Используем ту же логику, что и в /start
    project.address = request.address
    
    construction_site = db.query(ConstructionSite).filter(
        ConstructionSite.project_id == id
    ).first()
    
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
    
    chat = db.query(Chat).filter(
        Chat.project_id == id,
        Chat.is_active == True
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


@router.post("/{id}/reject-request", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def reject_request(
    id: UUID,
    request: RequestRejectRequest,
    db: Session = Depends(get_db)
):
    """
    Отклонить запрос на строительство
    
    Отклоняет запрос и возвращает проект в статус AVAILABLE.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    if project.status != ProjectStatus.REQUESTED:
        raise BadRequestError("Project is not in REQUESTED status")
    
    project.status = ProjectStatus.AVAILABLE
    # Причина отклонения передается в запросе, но не сохраняется в БД
    # Для сохранения причины можно добавить поле rejection_reason в модель Project
    db.commit()
    return None


@router.post("/batch-approve", response_model=List[ProjectResponse])
async def batch_approve_requests(
    request: BatchApproveRequest,
    db: Session = Depends(get_db)
):
    """
    Массовое одобрение запросов
    
    Одобряет несколько запросов одновременно.
    """
    projects = db.query(Project).filter(
        Project.id.in_(request.ids),
        Project.status == ProjectStatus.REQUESTED
    ).all()
    
    if len(projects) != len(request.ids):
        raise BadRequestError("Some projects not found or not in REQUESTED status")
    
    approved_projects = []
    for project in projects:
        construction_site = db.query(ConstructionSite).filter(
            ConstructionSite.project_id == project.id
        ).first()
        
        if not construction_site:
            construction_site = ConstructionSite(
                project_id=project.id,
                start_date=datetime.utcnow(),
                progress=0.0,
                all_documents_signed=False,
                is_completed=False,
            )
            db.add(construction_site)
            db.flush()
        
        chat = db.query(Chat).filter(
            Chat.project_id == project.id,
            Chat.is_active == True
        ).first()
        if not chat:
            chat = Chat(
                project_id=project.id,
                specialist_name="Ваш специалист",
                is_active=True
            )
            db.add(chat)
        
        project.status = ProjectStatus.CONSTRUCTION
        approved_projects.append(project)
    
    db.commit()
    for project in approved_projects:
        db.refresh(project)
    
    return approved_projects


# ==================== УПРАВЛЕНИЕ ПРОГРЕССОМ ====================

@router.patch("/construction-sites/{site_id}/progress", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def update_progress(
    site_id: UUID,
    request: ProgressUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Обновить прогресс строительства
    
    Обновляет прогресс строительной площадки (0.0 - 1.0).
    """
    site = db.query(ConstructionSite).filter(ConstructionSite.id == site_id).first()
    if not site:
        raise NotFoundError("ConstructionSite", str(site_id))
    
    site.progress = request.progress
    db.commit()
    return None


@router.patch("/construction-objects/{object_id}/stages/{stage_id}/status", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def update_object_stage_status(
    object_id: UUID,
    stage_id: UUID,
    request: StageStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Обновить статус этапа объекта строительства
    
    Обновляет статус этапа объекта (pending → in_progress → completed).
    """
    # Находим объект через construction_site (object_id = site.id)
    site = db.query(ConstructionSite).filter(ConstructionSite.id == object_id).first()
    if not site:
        raise NotFoundError("ConstructionSite", str(object_id))
    
    # Находим этап проекта
    stage = db.query(ProjectStage).filter(
        ProjectStage.id == stage_id,
        ProjectStage.project_id == site.project_id
    ).first()
    if not stage:
        raise NotFoundError("Stage", str(stage_id))
    
    try:
        stage.status = StageStatus(request.status)
    except ValueError:
        raise BadRequestError(f"Invalid status: {request.status}")
    
    stage.updated_at = datetime.utcnow()
    db.commit()
    return None


# ==================== АНАЛИТИКА ====================

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Получить общую статистику
    
    Возвращает статистику по проектам, документам и финансам.
    """
    # Статистика проектов
    total_projects = db.query(func.count(Project.id)).scalar() or 0
    available_projects = db.query(func.count(Project.id)).filter(
        Project.status == ProjectStatus.AVAILABLE
    ).scalar() or 0
    requested_projects = db.query(func.count(Project.id)).filter(
        Project.status == ProjectStatus.REQUESTED
    ).scalar() or 0
    in_progress_projects = db.query(func.count(Project.id)).filter(
        Project.status == ProjectStatus.CONSTRUCTION
    ).scalar() or 0
    
    # Статистика документов
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    pending_documents = db.query(func.count(Document.id)).filter(
        Document.status == DocumentStatus.PENDING
    ).scalar() or 0
    approved_documents = db.query(func.count(Document.id)).filter(
        Document.status == DocumentStatus.APPROVED
    ).scalar() or 0
    rejected_documents = db.query(func.count(Document.id)).filter(
        Document.status == DocumentStatus.REJECTED
    ).scalar() or 0
    
    # Финансовая статистика
    total_revenue_result = db.query(func.sum(Project.price)).filter(
        Project.status == ProjectStatus.CONSTRUCTION
    ).scalar()
    total_revenue = float(total_revenue_result) if total_revenue_result else 0.0
    
    average_price_result = db.query(func.avg(Project.price)).scalar()
    average_price = float(average_price_result) if average_price_result else 0.0
    
    return StatisticsResponse(
        totalProjects=total_projects,
        availableProjects=available_projects,
        requestedProjects=requested_projects,
        inProgressProjects=in_progress_projects,
        totalDocuments=total_documents,
        pendingDocuments=pending_documents,
        approvedDocuments=approved_documents,
        rejectedDocuments=rejected_documents,
        totalRevenue=total_revenue,
        averageProjectPrice=average_price
    )


# ==================== МАССОВЫЕ ОПЕРАЦИИ ====================

@router.post("/documents/batch-approve", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def batch_approve_documents(
    request: BatchApproveRequest,
    db: Session = Depends(get_db)
):
    """
    Массовое одобрение документов
    """
    documents = db.query(Document).filter(
        Document.id.in_(request.ids),
        Document.status == DocumentStatus.PENDING
    ).all()
    
    if len(documents) != len(request.ids):
        raise BadRequestError("Some documents not found or not in PENDING status")
    
    for document in documents:
        document.status = DocumentStatus.APPROVED
        document.approved_at = datetime.utcnow()
        document.rejection_reason = None
    
    db.commit()
    return None


@router.post("/documents/batch-reject", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def batch_reject_documents(
    request: BatchRejectRequest,
    db: Session = Depends(get_db)
):
    """
    Массовое отклонение документов
    """
    documents = db.query(Document).filter(
        Document.id.in_(request.ids),
        Document.status == DocumentStatus.PENDING
    ).all()
    
    if len(documents) != len(request.ids):
        raise BadRequestError("Some documents not found or not in PENDING status")
    
    for document in documents:
        document.status = DocumentStatus.REJECTED
        document.rejection_reason = request.reason
        document.approved_at = None
    
    db.commit()
    return None


# Импортируем ProjectStageResponse
from app.schemas.project import ProjectStageResponse
from app.models.construction_site import Camera
from app.schemas.construction_site import CameraResponse


# ==================== УПРАВЛЕНИЕ КАМЕРАМИ ====================

class CameraCreateRequest(BaseModel):
    """Схема создания камеры"""
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    stream_url: str = Field(..., min_length=1)
    thumbnail_url: Optional[str] = None


class CameraUpdateRequest(BaseModel):
    """Схема обновления камеры"""
    name: Optional[str] = None
    description: Optional[str] = None
    stream_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/construction-sites/{site_id}/cameras", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    site_id: UUID,
    request: CameraCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Добавить камеру на строительную площадку
    """
    site = db.query(ConstructionSite).filter(ConstructionSite.id == site_id).first()
    if not site:
        raise NotFoundError("ConstructionSite", str(site_id))
    
    camera = Camera(
        construction_site_id=site_id,
        name=request.name,
        description=request.description,
        stream_url=request.stream_url,
        thumbnail_url=request.thumbnail_url,
        is_active=True
    )
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.put("/construction-sites/{site_id}/cameras/{camera_id}", response_model=CameraResponse)
async def update_camera(
    site_id: UUID,
    camera_id: UUID,
    request: CameraUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Обновить камеру
    """
    site = db.query(ConstructionSite).filter(ConstructionSite.id == site_id).first()
    if not site:
        raise NotFoundError("ConstructionSite", str(site_id))
    
    camera = db.query(Camera).filter(
        Camera.id == camera_id,
        Camera.construction_site_id == site_id
    ).first()
    if not camera:
        raise NotFoundError("Camera", str(camera_id))
    
    if request.name is not None:
        camera.name = request.name
    if request.description is not None:
        camera.description = request.description
    if request.stream_url is not None:
        camera.stream_url = request.stream_url
    if request.thumbnail_url is not None:
        camera.thumbnail_url = request.thumbnail_url
    if request.is_active is not None:
        camera.is_active = request.is_active
    
    camera.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(camera)
    return camera


@router.delete("/construction-sites/{site_id}/cameras/{camera_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_camera(
    site_id: UUID,
    camera_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Удалить камеру
    """
    site = db.query(ConstructionSite).filter(ConstructionSite.id == site_id).first()
    if not site:
        raise NotFoundError("ConstructionSite", str(site_id))
    
    camera = db.query(Camera).filter(
        Camera.id == camera_id,
        Camera.construction_site_id == site_id
    ).first()
    if not camera:
        raise NotFoundError("Camera", str(camera_id))
    
    db.delete(camera)
    db.commit()
    return None


# ==================== УВЕДОМЛЕНИЯ ====================

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Получить список уведомлений
    
    Возвращает уведомления для администратора на основе данных из БД.
    Уведомления генерируются динамически из запрошенных проектов и документов на согласовании.
    Для полноценной реализации с историей и статусом прочтения можно добавить модель Notification в БД.
    """
    notifications = []
    
    # Уведомления о новых запросах
    requested_projects = db.query(Project).filter(
        Project.status == ProjectStatus.REQUESTED
    ).all()
    for project in requested_projects:
        notifications.append(NotificationResponse(
            id=project.id,  # Временный ID
            type="new_request",
            title="Новый запрос на строительство",
            message=f"Проект '{project.name}' запрошен на строительство",
            projectId=project.id,
            isRead=False,
            createdAt=project.created_at
        ))
    
    # Уведомления о новых документах
    pending_documents = db.query(Document).filter(
        Document.status == DocumentStatus.PENDING
    ).all()
    for document in pending_documents:
        notifications.append(NotificationResponse(
            id=document.id,  # Временный ID
            type="new_document",
            title="Новый документ на согласование",
            message=f"Документ '{document.title}' требует согласования",
            projectId=document.project_id,
            documentId=document.id,
            isRead=False,
            createdAt=document.submitted_at or document.created_at
        ))
    
    # Сортируем по дате (новые первыми)
    notifications.sort(key=lambda n: n.createdAt, reverse=True)
    
    if unread_only:
        notifications = [n for n in notifications if not n.isRead]
    
    return notifications[:50]  # Ограничиваем 50 уведомлениями


@router.post("/notifications/{notification_id}/read", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Отметить уведомление как прочитанное
    
    В текущей реализации уведомления генерируются динамически, поэтому отметка прочтения
    не сохраняется в БД. Для сохранения статуса прочтения можно добавить модель Notification в БД.
    """
    # В текущей реализации уведомления генерируются динамически,
    # поэтому отметка прочтения не сохраняется. Возвращаем успех для совместимости API.
    return None

