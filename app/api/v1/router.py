from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    projects,
    documents,
    construction_sites,
    construction_objects,
    chats,
    completion,
    admin,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# Подключение роутеров для каждого модуля
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(
    construction_sites.router,
    prefix="/construction-sites",
    tags=["construction-sites"]
)
api_router.include_router(
    construction_objects.router,
    prefix="/construction-objects",
    tags=["construction-objects"]
)
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(completion.router, prefix="/projects", tags=["completion"])
# Админские эндпоинты
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

