from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
import app.models # Ensure models are loaded
from app.api import (
    documents_router,
    chat_router,
    dashboard_router,
    search_router,
    settings_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    Base.metadata.create_all(bind=engine)
    print(f"[Startup] SQLite database initialized at {settings.DATABASE_URL}")
    print(f"[Startup] Vector Store Chroma initialized at {settings.CHROMA_DIR}")
    yield
    print("[Shutdown] Cleaning up application resources.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Enterprise-grade Retrieval-Augmented Generation (RAG) platform with document ingestion, vector search, and AI question answering.",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(search_router, prefix=settings.API_PREFIX)
app.include_router(settings_router, prefix=settings.API_PREFIX)

@app.get("/api/health", tags=["system"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION
    }

@app.get("/", tags=["system"])
def root():
    return {
        "message": "Welcome to Intelligent Knowledge Retrieval and Question Answering API",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }

