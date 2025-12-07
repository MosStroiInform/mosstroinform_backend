from fastapi import HTTPException, status
from typing import Optional


class APIException(HTTPException):
    """Базовый класс для ошибок API с единым форматом"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: Optional[str] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code,
                    "message": message
                }
            }
        )


class NotFoundError(APIException):
    """Ошибка 404 - ресурс не найден"""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message
        )


class BadRequestError(APIException):
    """Ошибка 400 - некорректный запрос"""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            message=message
        )


class InternalServerError(APIException):
    """Ошибка 500 - внутренняя ошибка сервера"""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            message=message
        )

