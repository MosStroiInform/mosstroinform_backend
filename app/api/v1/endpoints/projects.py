from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.project import Project
from app.schemas.project import ProjectResponse, EmptyResponse

router = APIRouter()


@router.get("", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    """
    Получить список всех проектов строительства
    
    Возвращает список всех доступных проектов с их этапами.
    """
    projects = db.query(Project).all()
    return projects


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


@router.post("/{id}/request", response_model=EmptyResponse, status_code=status.HTTP_200_OK)
async def request_construction(id: UUID, db: Session = Depends(get_db)):
    """
    Отправить запрос на строительство проекта
    
    Отправляет запрос на начало строительства проекта.
    В текущей версии просто возвращает успешный ответ.
    В будущем здесь может быть логика проверки статуса проекта.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise NotFoundError("Project", str(id))
    
    # TODO: В будущем здесь можно добавить проверку статуса проекта
    # Например, проверить, не начато ли уже строительство
    
    return EmptyResponse()
