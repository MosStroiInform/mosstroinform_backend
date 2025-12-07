from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from uuid import UUID

from app.schemas.base import BaseSchema


class ProjectStageResponse(BaseSchema):
    """Схема этапа проекта для ответа"""
    id: UUID
    name: str
    status: str  # "pending" | "in_progress" | "completed"


class ProjectResponse(BaseSchema):
    """Схема проекта для ответа"""
    id: UUID
    name: str
    address: str
    description: str = ""  # Мобильное приложение ожидает обязательное поле
    area: float
    floors: int
    price: int  # Мобильное приложение ожидает int, а не float
    imageUrl: Optional[str] = Field(None, alias="image_url")
    bedrooms: int = 0
    bathrooms: int = 0
    status: str = "available"
    objectId: Optional[UUID] = Field(None, alias="object_id")
    stages: List[ProjectStageResponse] = []
    
    @field_validator('description', mode='before')
    @classmethod
    def convert_description(cls, v: Any) -> str:
        """Конвертирует None в пустую строку для description"""
        if v is None:
            return ""
        return str(v)
    
    @field_validator('price', mode='before')
    @classmethod
    def convert_price_to_int(cls, v: Any) -> int:
        """Конвертирует float в int для price"""
        if isinstance(v, float):
            return int(v)
        return int(v)


class ProjectStartRequest(BaseModel):
    """Схема запроса на запуск строительства проекта"""
    address: str = Field(..., min_length=1)

