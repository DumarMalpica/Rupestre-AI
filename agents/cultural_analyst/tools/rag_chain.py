from __future__ import annotations


def build_prompt(
    detected_motifs: list,
    similar_motifs: list,
    site_name: str,
    coordinates: tuple,
) -> str:
    motif_lines = (
        "\n".join(
            f"  - {m['clase']} (confianza: {m['confidence']:.2f})"
            for m in detected_motifs
        )
        or "  (ninguno detectado)"
    )

    parallel_lines: list[str] = []
    for entry in similar_motifs:
        for match in entry.get("top_matches", []):
            parallel_lines.append(
                f"  - {match['site']}: {match['cultura']}, "
                f"{match['periodo']} (similitud: {match['score']:.2f})"
            )
    parallels_text = (
        "\n".join(parallel_lines)
        if parallel_lines
        else "  No se encontraron paralelos en el corpus."
    )

    lat, lon = coordinates

    return (
        f"Eres un arqueólogo especialista en arte rupestre colombiano.\n\n"
        f"Sitio: {site_name}\n"
        f"Coordenadas: {lat:.4f}N, {lon:.4f}W\n\n"
        f"Motivos rupestres detectados:\n{motif_lines}\n\n"
        f"Paralelos iconográficos en el corpus:\n{parallels_text}\n\n"
        f"Proporciona una interpretación arqueológica fundamentada de los motivos, "
        f"citando fuentes del corpus cuando sea posible. Considera el contexto "
        f"cultural, cronológico y ritual del sitio."
    )
