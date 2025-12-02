from pydantic import BaseModel, field_validator
from typing import Any
import enum


class BaseSchema(BaseModel):
    """Базовая схема с поддержкой сериализации Enum"""
    
    class Config:
        from_attributes = True
        populate_by_name = True
    
    @field_validator('*', mode='before')
    @classmethod
    def convert_enum_to_value(cls, v: Any) -> Any:
        """Конвертирует Enum в строковое значение"""
        if isinstance(v, enum.Enum):
            return v.value
        return v


class EmptyResponse(BaseModel):
    """Пустой ответ для POST запросов"""
    pass

