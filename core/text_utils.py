from __future__ import annotations

import re


def clean_interpretation(text: str) -> str:
    """Limpia el markdown que produce el LLM para mostrar prosa ordenada.

    Quita negritas (**x**), encabezados (#), viñetas con asteriscos y backticks.
    El resultado es texto plano legible en PDF, HTML y WhatsApp por igual.
    """
    if not text:
        return ""

    t = text.replace("\r\n", "\n")
    # Viñetas markdown al inicio de línea → •
    t = re.sub(r"^[ \t]*[-*+]\s+", "• ", t, flags=re.MULTILINE)
    # Encabezados markdown (## Título) → Título
    t = re.sub(r"^#{1,6}\s*", "", t, flags=re.MULTILINE)
    # Negrita/itálica *x* **x** ***x***
    t = re.sub(r"\*{1,3}([^*\n]+?)\*{1,3}", r"\1", t)
    t = re.sub(r"__([^_\n]+?)__", r"\1", t)
    # Asteriscos/backticks sueltos remanentes
    t = t.replace("*", "").replace("`", "")
    # Colapsa saltos de línea excesivos
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()
