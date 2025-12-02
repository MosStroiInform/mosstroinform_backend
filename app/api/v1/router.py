from fastapi import APIRouter
from app.api.v1.endpoints import projects, documents, construction_sites, chats, completion

api_router = APIRouter()

# Подключение роутеров для каждого модуля
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(
    construction_sites.router,
    prefix="/construction-sites",
    tags=["construction-sites"]
)
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(completion.router, prefix="/projects", tags=["completion"])

