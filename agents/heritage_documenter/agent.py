import os
import uuid

from core.logger import get_logger, langfuse_context, observe
from core.config import settings
from core.exceptions import AgentExecutionError
from core.state import RupestreState
from agents.heritage_documenter.tools.json_builder import build_ficha_json
from agents.heritage_documenter.tools.template_engine import render_html
from agents.heritage_documenter.tools.pdf_generator import generate_pdf

logger = get_logger("heritage_documenter")


@observe(name="build_json")
def _json_span(state: RupestreState, record_id: str) -> dict:
    ficha_json = build_ficha_json(state, record_id)
    langfuse_context.update_current_observation(
        output={"record_id": record_id, "fields": len(ficha_json)}
    )
    return ficha_json


@observe(name="render_html")
def _html_span(ficha_json: dict) -> str:
    html = render_html(ficha_json)
    langfuse_context.update_current_observation(
        output={"html_length": len(html)}
    )
    return html


@observe(name="generate_pdf")
def _pdf_span(ficha_json: dict, pdf_path: str) -> None:
    generate_pdf(ficha_json, pdf_path)
    langfuse_context.update_current_observation(
        output={"pdf_path": pdf_path}
    )


@observe(name="ag6_heritage_documenter")
def heritage_documenter_node(state: RupestreState) -> dict:
    langfuse_context.update_current_trace(
        session_id=state.get("session_id", "default"),
        input={"site_name": state.get("site_name"),
               "motif_count": state.get("motif_count", 0)},
        tags=["rupestre-ai", "ag6"],
    )

    try:
        record_id = str(uuid.uuid4())[:8].upper()
        os.makedirs(settings.output_dir, exist_ok=True)

        ficha_json = _json_span(state, record_id)
        _html_span(ficha_json)  # html medido en el span, no necesario para generate_pdf

        pdf_path = f"{settings.output_dir}/{record_id}_ficha_icanh.pdf"
        _pdf_span(ficha_json, pdf_path)

        logger.info(f"Ficha ICANH generada: {record_id} → {pdf_path}")
        result = {"ficha_pdf_path": pdf_path,
                  "ficha_json": ficha_json,
                  "record_id": record_id,
                  "current_agent": "heritage_documenter"}
        langfuse_context.update_current_trace(
            output={"record_id": record_id, "pdf_generated": True}
        )
        return result

    except Exception as exc:
        logger.error(f"Error en heritage_documenter_node: {exc}")
        langfuse_context.update_current_trace(
            output={"error": str(exc)}, level="ERROR"
        )
        raise AgentExecutionError("heritage_documenter", str(exc)) from exc
