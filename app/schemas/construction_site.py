from pydantic import Field, field_validator
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID

from app.schemas.base import BaseSchema


class CameraResponse(BaseSchema):
    """Схема камеры для ответа"""
    id: UUID
    name: str
    description: str = ""  # Мобильное приложение ожидает обязательное поле
    streamUrl: str = Field(..., alias="stream_url")
    isActive: bool = Field(..., alias="is_active")
    thumbnailUrl: Optional[str] = Field(None, alias="thumbnail_url")
    
    @field_validator('description', mode='before')
    @classmethod
    def convert_description(cls, v: Any) -> str:
        """Конвертирует None в пустую строку для description"""
        if v is None:
            return ""
        return str(v)


class ConstructionSiteResponse(BaseSchema):
    """Схема строительной площадки для ответа"""
    id: UUID
    projectId: UUID = Field(..., alias="project_id")
    projectName: str = Field(..., alias="project_name")
    address: str
    cameras: List[CameraResponse] = []
    startDate: Optional[datetime] = Field(None, alias="start_date")
    expectedCompletionDate: Optional[datetime] = Field(None, alias="expected_completion_date")
    progress: float = Field(..., ge=0.0, le=1.0)


class ConstructionObjectStageResponse(BaseSchema):
    """Схема этапа для объекта строительства (повторяет этап проекта)"""
    id: UUID
    name: str
    status: str


class ConstructionObjectResponse(BaseSchema):
    """Схема объекта строительства для ответа"""
    id: UUID
    projectId: UUID = Field(..., alias="project_id")
    name: str
    address: str
    description: str = ""
    area: float
    floors: int
    bedrooms: int = 0
    bathrooms: int = 0
    price: int
    imageUrl: Optional[str] = Field(None, alias="image_url")
    stages: List[ConstructionObjectStageResponse] = []
    chatId: Optional[UUID] = Field(None, alias="chat_id")
    allDocumentsSigned: bool = Field(False, alias="all_documents_signed")
    isCompleted: bool = Field(False, alias="is_completed")


class DocumentsStatusUpdateRequest(BaseSchema):
    """Схема обновления статуса подписания документов объекта"""
    allDocumentsSigned: bool = Field(..., alias="allDocumentsSigned")
