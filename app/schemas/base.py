from pydantic import BaseModel, field_validator, ConfigDict
from typing import Any
import enum


class BaseSchema(BaseModel):
    """Базовая схема с поддержкой сериализации Enum и camelCase"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        # Используем имя поля (camelCase) для сериализации JSON
        # alias используется только для чтения из snake_case
    )
    
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

