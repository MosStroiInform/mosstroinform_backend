from app.schemas.base import BaseSchema, EmptyResponse
from app.schemas.project import (
    ProjectResponse,
    ProjectStageResponse,
    ProjectStartRequest,
)
from app.schemas.document import (
    DocumentResponse,
    DocumentRejectRequest,
)
from app.schemas.construction_site import (
    ConstructionSiteResponse,
    CameraResponse,
    ConstructionObjectResponse,
    ConstructionObjectStageResponse,
    DocumentsStatusUpdateRequest,
)
from app.schemas.chat import (
    ChatResponse,
    MessageResponse,
    MessageCreateRequest,
)
from app.schemas.completion import (
    CompletionStatusResponse,
    FinalDocumentResponse,
    FinalDocumentRejectRequest,
)
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    UserResponse,
)

__all__ = [
    "BaseSchema",
    "EmptyResponse",
    "ProjectResponse",
    "ProjectStageResponse",
    "ProjectStartRequest",
    "DocumentResponse",
    "DocumentRejectRequest",
    "ConstructionSiteResponse",
    "CameraResponse",
    "ConstructionObjectResponse",
    "ConstructionObjectStageResponse",
    "DocumentsStatusUpdateRequest",
    "ChatResponse",
    "MessageResponse",
    "MessageCreateRequest",
    "CompletionStatusResponse",
    "FinalDocumentResponse",
    "FinalDocumentRejectRequest",
    "AuthResponse",
    "LoginRequest",
    "RegisterRequest",
    "RefreshRequest",
    "UserResponse",
]
