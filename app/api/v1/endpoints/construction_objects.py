from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.construction_site import ConstructionSite
from app.models.project import Project
from app.models.chat import Chat
from app.schemas.construction_site import (
    ConstructionObjectResponse,
    DocumentsStatusUpdateRequest,
)

router = APIRouter()


def _build_object_response(
    construction_site: ConstructionSite,
    project: Project,
    chat_id,
) -> ConstructionObjectResponse:
    """Собирает объект ответа для construction-objects"""
    return ConstructionObjectResponse(
        id=construction_site.id,
        project_id=project.id,
        name=project.name,
        address=project.address,
        description=project.description or "",
        area=project.area,
        floors=project.floors,
        bedrooms=project.bedrooms,
        bathrooms=project.bathrooms,
        price=int(project.price),
        image_url=project.image_url,
        stages=project.stages,
        chat_id=chat_id,
        all_documents_signed=construction_site.all_documents_signed,
        is_completed=construction_site.is_completed,
    )


@router.get("", response_model=List[ConstructionObjectResponse])
async def get_construction_objects(db: Session = Depends(get_db)):
    """
    Получить список всех объектов строительства текущего пользователя.
    В текущей версии возвращаются все объекты.
    """
    construction_sites = db.query(ConstructionSite).all()
    result: List[ConstructionObjectResponse] = []

    for site in construction_sites:
        project = db.query(Project).filter(Project.id == site.project_id).first()
        if not project:
            raise NotFoundError("Project", str(site.project_id))

        chat = db.query(Chat).filter(
            Chat.project_id == project.id,
            Chat.is_active == True,  # noqa: E712
        ).order_by(Chat.created_at).first()

        result.append(_build_object_response(site, project, chat.id if chat else None))
    # Отдаем данные с alias (camelCase), как ожидает мобильное приложение
    return [item.model_dump(by_alias=True) for item in result]


@router.get("/{object_id}", response_model=ConstructionObjectResponse)
async def get_construction_object(
    object_id: UUID,
    db: Session = Depends(get_db)
):
    """Получить информацию о конкретном объекте строительства."""
    construction_site = db.query(ConstructionSite).filter(
        ConstructionSite.id == object_id
    ).first()
    if not construction_site:
        raise NotFoundError("Construction site", str(object_id))

    project = db.query(Project).filter(Project.id == construction_site.project_id).first()
    if not project:
        raise NotFoundError("Project", str(construction_site.project_id))

    chat = db.query(Chat).filter(
        Chat.project_id == project.id,
        Chat.is_active == True,  # noqa: E712
    ).order_by(Chat.created_at).first()

    response = _build_object_response(construction_site, project, chat.id if chat else None)
    # Отдаем данные с alias (camelCase), как ожидает мобильное приложение
    return response.model_dump(by_alias=True)


@router.post(
    "/{object_id}/complete",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def complete_construction_object(
    object_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Завершить строительство объекта.
    Требует, чтобы все документы были подписаны и прогресс достиг 100%.
    """
    construction_site = db.query(ConstructionSite).filter(
        ConstructionSite.id == object_id
    ).first()
    if not construction_site:
        raise NotFoundError("Construction site", str(object_id))

    if construction_site.is_completed:
        return None

    if not construction_site.all_documents_signed:
        raise BadRequestError("All documents must be signed before completion")

    if construction_site.progress < 1.0:
        raise BadRequestError("Construction progress must be 100% to complete")

    construction_site.is_completed = True
    construction_site.updated_at = datetime.utcnow()
    db.commit()
    return None


@router.patch(
    "/by-project/{project_id}/documents-status",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_documents_status(
    project_id: UUID,
    request: DocumentsStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Обновить статус подписания документов для объекта строительства.
    """
    construction_site = db.query(ConstructionSite).filter(
        ConstructionSite.project_id == project_id
    ).first()
    if not construction_site:
        raise NotFoundError("Construction site", f"for project {project_id}")

    construction_site.all_documents_signed = request.allDocumentsSigned

    db.commit()
    return None

