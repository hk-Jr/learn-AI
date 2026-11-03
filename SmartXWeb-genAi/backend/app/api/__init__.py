from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.dashboard import router as dashboard_router
from app.api.search import router as search_router
from app.api.settings import router as settings_router

__all__ = [
    "documents_router",
    "chat_router",
    "dashboard_router",
    "search_router",
    "settings_router"
]

