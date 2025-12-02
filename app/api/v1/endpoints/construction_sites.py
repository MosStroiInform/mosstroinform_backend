from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.models.construction_site import ConstructionSite, Camera
from app.models.project import Project
from app.schemas.construction_site import ConstructionSiteResponse, CameraResponse

router = APIRouter()


@router.get("/project/{project_id}", response_model=ConstructionSiteResponse)
async def get_construction_site_by_project(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получить информацию о строительной площадке по проекту
    
    Возвращает информацию о строительной площадке для указанного проекта,
    включая список камер.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundError("Project", str(project_id))
    
    construction_site = db.query(ConstructionSite).filter(
        ConstructionSite.project_id == project_id
    ).first()
    
    if not construction_site:
        raise NotFoundError("Construction site", f"for project {project_id}")
    
    # Создаем ответ с вычисляемыми полями из проекта
    response_data = {
        "id": construction_site.id,
        "project_id": construction_site.project_id,
        "project_name": project.name,
        "address": project.address,
        "cameras": construction_site.cameras,
        "start_date": construction_site.start_date,
        "expected_completion_date": construction_site.expected_completion_date,
        "progress": construction_site.progress,
    }
    
    return ConstructionSiteResponse(**response_data)


@router.get("/{site_id}/cameras", response_model=List[CameraResponse])
async def get_cameras(
    site_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получить список камер строительной площадки
    
    Возвращает список всех камер для указанной строительной площадки.
    """
    construction_site = db.query(ConstructionSite).filter(
        ConstructionSite.id == site_id
    ).first()
    
    if not construction_site:
        raise NotFoundError("Construction site", str(site_id))
    
    cameras = db.query(Camera).filter(
        Camera.construction_site_id == site_id
    ).all()
    
    return cameras


@router.get("/{site_id}/cameras/{camera_id}", response_model=CameraResponse)
async def get_camera(
    site_id: UUID,
    camera_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получить информацию о камере
    
    Возвращает детальную информацию о конкретной камере строительной площадки.
    """
    construction_site = db.query(ConstructionSite).filter(
        ConstructionSite.id == site_id
    ).first()
    
    if not construction_site:
        raise NotFoundError("Construction site", str(site_id))
    
    camera = db.query(Camera).filter(
        Camera.id == camera_id,
        Camera.construction_site_id == site_id
    ).first()
    
    if not camera:
        raise NotFoundError("Camera", str(camera_id))
    
    return camera
