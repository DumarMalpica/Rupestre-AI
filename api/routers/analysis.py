"""Endpoint principal: dispara el grafo LangGraph."""

import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from api.schemas.request import AnalysisRequest
from api.schemas.response import AnalysisResponse, RecordResponse
from core.logger import get_logger

logger = get_logger("api.analysis")
router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_site(
    image: UploadFile = File(..., description="Fotografía del sitio rupestre"),
    site_name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
):
    """
    Recibe imagen + metadatos y dispara el pipeline completo de análisis.
    Retorna un session_id para consultar el resultado posterior.
    """
    session_id = str(uuid.uuid4())
    logger.info(f"Nueva sesión: {session_id} | Sitio: {site_name}")

    # TODO: guardar imagen en MinIO y encolar en Celery
    # image_path = await storage.save(image, session_id)
    # celery_task.delay(session_id, image_path, site_name, latitude, longitude)

    return AnalysisResponse(
        session_id=session_id,
        status="pending",
        message=f"Análisis iniciado para {site_name}. Consulta el resultado con el session_id.",
    )


@router.get("/records/{record_id}", response_model=RecordResponse)
async def get_record(record_id: str):
    """Retorna la ficha ICANH generada por el pipeline."""
    # TODO: consultar en PostgreSQL por record_id
    raise HTTPException(status_code=404, detail=f"Registro {record_id} no encontrado")
