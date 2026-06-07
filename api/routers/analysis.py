from __future__ import annotations

import os
import time
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from api.schemas.response import AnalyzeResponse, RecordResponse
from core.config import settings
from core.graph import rupestre_graph
from core.state import RupestreState

router = APIRouter(prefix="/api")

# Almacén en memoria de fichas completas.
# En producción reemplazar por consulta a PostgreSQL.
_records: dict[str, dict] = {}


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    image: UploadFile = File(..., description="Imagen JPG/PNG del sitio rupestre"),
    site_name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    department: str = Form("No especificado"),
    municipality: str = Form("No especificado"),
) -> AnalyzeResponse:
    t0 = time.perf_counter()

    # Guardar imagen recibida
    os.makedirs(settings.samples_dir, exist_ok=True)
    safe_name = image.filename or "upload.jpg"
    img_path = os.path.join(settings.samples_dir, f"{uuid.uuid4()}_{safe_name}")
    content = await image.read()
    with open(img_path, "wb") as fh:
        fh.write(content)

    # Estado inicial del pipeline
    state: RupestreState = {
        "image_path": img_path,
        "site_name": site_name,
        "department": department,
        "municipality": municipality,
        "coordinates": (latitude, longitude),
        "session_id": str(uuid.uuid4()),
        "errors": [],
        "current_agent": "",
    }

    result = rupestre_graph.invoke(state)
    elapsed = round(time.perf_counter() - t0, 2)

    # Imagen rechazada por control de calidad
    if not result.get("image_quality_ok", True):
        errors = result.get("errors", [])
        detail = errors[0] if errors else "Calidad de imagen insuficiente"
        raise HTTPException(status_code=422, detail=detail)

    record_id: str = result.get("record_id", "")
    ficha_json: dict = result.get("ficha_json", {})

    if record_id and ficha_json:
        _records[record_id] = ficha_json

    pdf_path: str = result.get("ficha_pdf_path", "")

    return AnalyzeResponse(
        record_id=record_id,
        motif_count=result.get("motif_count", 0),
        cultural_interpretation=result.get("cultural_interpretation", ""),
        interpretation_confidence=result.get("interpretation_confidence", 0.0),
        reconstruction_applied=result.get("reconstruction_applied", False),
        pdf_available=bool(pdf_path) and os.path.isfile(pdf_path),
        requires_human_review=result.get("requires_human_review", False),
        processing_time_seconds=elapsed,
    )


@router.get("/records/{record_id}", response_model=RecordResponse)
def get_record(record_id: str) -> RecordResponse:
    ficha = _records.get(record_id)
    if ficha is None:
        raise HTTPException(
            status_code=404, detail=f"Registro '{record_id}' no encontrado"
        )

    pdf_path = os.path.join(settings.output_dir, f"{record_id}_ficha_icanh.pdf")
    return RecordResponse(**ficha, pdf_available=os.path.isfile(pdf_path))


@router.get("/records/{record_id}/pdf")
def get_record_pdf(record_id: str) -> FileResponse:
    pdf_path = os.path.join(settings.output_dir, f"{record_id}_ficha_icanh.pdf")
    if not os.path.isfile(pdf_path):
        raise HTTPException(
            status_code=404,
            detail=f"PDF para registro '{record_id}' no disponible",
        )
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{record_id}_ficha_icanh.pdf",
    )
