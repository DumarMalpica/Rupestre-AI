from __future__ import annotations

import os
import uuid

from core.config import settings
from core.exceptions import AgentExecutionError
from core.logger import get_logger
from core.state import RupestreState

from agents.heritage_documenter.tools.json_builder import build_ficha_json
from agents.heritage_documenter.tools.pdf_generator import generate_pdf
from agents.heritage_documenter.tools.template_engine import render_html

logger = get_logger("heritage_documenter")


def heritage_documenter_node(state: RupestreState) -> dict:
    try:
        record_id = str(uuid.uuid4())[:8].upper()
        os.makedirs(settings.output_dir, exist_ok=True)

        ficha_json = build_ficha_json(state, record_id)
        html = render_html(ficha_json)

        pdf_path = os.path.join(
            settings.output_dir, f"{record_id}_ficha_icanh.pdf"
        )
        generate_pdf(ficha_json, pdf_path)

        logger.info("Ficha ICANH generada: %s → %s", record_id, pdf_path)

        return {
            "ficha_pdf_path": pdf_path,
            "ficha_json": ficha_json,
            "record_id": record_id,
            "current_agent": "heritage_documenter",
        }

    except Exception as exc:
        logger.exception("Error en heritage_documenter_node")
        raise AgentExecutionError("heritage_documenter", str(exc)) from exc
