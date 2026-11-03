from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.settings import SystemSetting
from app.schemas.settings import SettingsResponse, SettingsUpdateRequest
from app.config import settings

router = APIRouter(prefix="/settings", tags=["settings"])

def _get_val(db: Session, key: str, default: str) -> str:
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    return s.value if s else default

def _set_val(db: Session, key: str, value: str):
    s = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if s:
        s.value = value
    else:
        s = SystemSetting(key=key, value=value)
        db.add(s)
    db.commit()

@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Retrieve system configuration without leaking raw secret keys."""
    llm_provider = _get_val(db, "llm_provider", settings.DEFAULT_LLM_PROVIDER)
    llm_model = _get_val(db, "llm_model", settings.DEFAULT_LLM_MODEL)
    embedding_provider = _get_val(db, "embedding_provider", settings.DEFAULT_EMBEDDING_PROVIDER)
    embedding_model = _get_val(db, "embedding_model", settings.DEFAULT_EMBEDDING_MODEL)
    chunk_size = int(_get_val(db, "chunk_size", str(settings.DEFAULT_CHUNK_SIZE)))
    chunk_overlap = int(_get_val(db, "chunk_overlap", str(settings.DEFAULT_CHUNK_OVERLAP)))
    top_k = int(_get_val(db, "top_k", str(settings.DEFAULT_TOP_K)))
    similarity_threshold = float(_get_val(db, "similarity_threshold", str(settings.DEFAULT_SIMILARITY_THRESHOLD)))
    
    gemini_key = _get_val(db, "gemini_api_key", settings.GEMINI_API_KEY)
    openai_key = _get_val(db, "openai_api_key", settings.OPENAI_API_KEY)
    ollama_url = _get_val(db, "ollama_base_url", settings.OLLAMA_BASE_URL)

    return SettingsResponse(
        llm_provider=llm_provider,
        llm_model=llm_model,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
        has_gemini_key=bool(gemini_key and len(gemini_key) > 5),
        has_openai_key=bool(openai_key and len(openai_key) > 5),
        ollama_base_url=ollama_url
    )

@router.put("", response_model=SettingsResponse)
def update_settings(update: SettingsUpdateRequest, db: Session = Depends(get_db)):
    """Update system settings and API credentials safely."""
    if update.llm_provider is not None:
        _set_val(db, "llm_provider", update.llm_provider)
    if update.llm_model is not None:
        _set_val(db, "llm_model", update.llm_model)
    if update.embedding_provider is not None:
        _set_val(db, "embedding_provider", update.embedding_provider)
    if update.embedding_model is not None:
        _set_val(db, "embedding_model", update.embedding_model)
    if update.chunk_size is not None:
        _set_val(db, "chunk_size", str(update.chunk_size))
    if update.chunk_overlap is not None:
        _set_val(db, "chunk_overlap", str(update.chunk_overlap))
    if update.top_k is not None:
        _set_val(db, "top_k", str(update.top_k))
    if update.similarity_threshold is not None:
        _set_val(db, "similarity_threshold", str(update.similarity_threshold))
    if update.gemini_api_key is not None and update.gemini_api_key.strip():
        _set_val(db, "gemini_api_key", update.gemini_api_key.strip())
    if update.openai_api_key is not None and update.openai_api_key.strip():
        _set_val(db, "openai_api_key", update.openai_api_key.strip())
    if update.ollama_base_url is not None:
        _set_val(db, "ollama_base_url", update.ollama_base_url.strip())

    return get_settings(db)

@router.get("/ollama-models")
def get_ollama_models(db: Session = Depends(get_db)):
    """Discover available local Ollama models."""
    from app.services.llm_service import LLMService
    ollama_url = _get_val(db, "ollama_base_url", settings.OLLAMA_BASE_URL)
    models = LLMService.get_available_ollama_models(ollama_url)
    return {"ollama_url": ollama_url, "available_models": models}


