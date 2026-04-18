"""Aplicación FastAPI principal de Rupestre AI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import analysis
from core.logger import get_logger

logger = get_logger("api.main")

app = FastAPI(
    title="Rupestre AI API",
    description="Sistema de IA para reconstrucción de arte rupestre andino colombiano",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)


@app.get("/health")
def health():
    """Health check del servicio."""
    return {"status": "ok", "service": "rupestre-ai"}


if __name__ == "__main__":
    import uvicorn
    from core.config import settings
    uvicorn.run("api.main:app", host=settings.api_host, port=settings.api_port, reload=True)
