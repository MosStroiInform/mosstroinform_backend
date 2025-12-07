from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

from app.core.config import settings
from app.core.exceptions import APIException
from app.api.v1.router import api_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (для работы с мобильным приложением)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Обработчик исключений API
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Обработчик для кастомных исключений API"""
    logger.warning(f"API Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


# Обработчик HTTPException (включая стандартные FastAPI исключения)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик для стандартных HTTP исключений"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail) if not isinstance(exc.detail, dict) else exc.detail.get("error", {}).get("message", str(exc.detail))
            }
        }
    )


# Обработчик ошибок валидации Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик для ошибок валидации запросов"""
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )


# Обработчик общих исключений
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик для неожиданных исключений"""
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error"
            }
        }
    )


# Подключение роутеров API
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работы API"""
    return {
        "message": "MosStroiInform API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Эндпоинт для проверки здоровья приложения"""
    return {"status": "ok"}
