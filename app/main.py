from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import APIException
from app.api.v1.router import api_router

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
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


# Обработчик общих исключений
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Обработчик для неожиданных исключений"""
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
