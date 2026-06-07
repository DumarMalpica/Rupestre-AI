from __future__ import annotations


def build_prompt(
    detected_motifs: list,
    similar_motifs: list,
    site_name: str,
    coordinates: tuple,
    image_description: str = "",
    corpus_passages: list | None = None,
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

    corpus_passages = corpus_passages or []
    passage_lines = (
        "\n\n".join(
            f"  [{p['source']}, p.{p['page']}] {p['text']}" for p in corpus_passages
        )
        or "  (sin pasajes recuperados del corpus)"
    )

    description_block = image_description.strip() or "  (sin descripción visual)"

    lat, lon = coordinates

    return (
        f"Eres un arqueólogo especialista en arte rupestre colombiano.\n\n"
        f"Sitio: {site_name}\n"
        f"Coordenadas: {lat:.4f}N, {lon:.4f}W\n\n"
        f"Descripción visual del pictograma:\n{description_block}\n\n"
        f"Motivos rupestres detectados:\n{motif_lines}\n\n"
        f"Paralelos iconográficos en el corpus:\n{parallels_text}\n\n"
        f"Fragmentos relevantes del corpus documental:\n{passage_lines}\n\n"
        f"Proporciona una interpretación arqueológica fundamentada de los motivos, "
        f"citando los fragmentos del corpus (autor/obra) cuando los uses. Considera "
        f"el contexto cultural, cronológico y ritual del sitio. No inventes fuentes "
        f"que no aparezcan en los fragmentos proporcionados.\n\n"
        f"Escribe en prosa clara y ordenada, en 2 o 3 párrafos cortos. NO uses "
        f"formato markdown: nada de asteriscos (**), almohadillas (#) ni viñetas. "
        f"Los nombres propios van en texto normal."
    )
