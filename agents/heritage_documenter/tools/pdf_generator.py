"""
AG6 — Heritage Documenter: PDF Generator
Genera ficha ICANH profesional usando ReportLab.
"""
import os
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


# ── Paleta de colores ──────────────────────────────────────────────────────────
DARK       = colors.HexColor("#1a1a2e")
PRIMARY    = colors.HexColor("#c0392b")   # rojo ICANH
ACCENT     = colors.HexColor("#e67e22")   # naranja paralelos
LIGHT_GRAY = colors.HexColor("#f5f5f5")
MID_GRAY   = colors.HexColor("#e0e0e0")
TEXT_GRAY  = colors.HexColor("#666666")
WHITE      = colors.white
TEAL       = colors.HexColor("#16a085")   # confianza alta
WARM_BG    = colors.HexColor("#fef9f0")   # fondo interpretación


W, H = A4
MARGIN = 18 * mm


# ── Estilos de texto ───────────────────────────────────────────────────────────
def _styles():
    base = ParagraphStyle
    return {
        "title":      base("title",      fontName="Helvetica-Bold",   fontSize=18, textColor=DARK,      leading=22),
        "subtitle":   base("subtitle",   fontName="Helvetica",        fontSize=9,  textColor=TEXT_GRAY, leading=12),
        "section":    base("section",    fontName="Helvetica-Bold",   fontSize=8,  textColor=TEXT_GRAY, leading=10, spaceAfter=4),
        "card_label": base("card_label", fontName="Helvetica",        fontSize=7,  textColor=TEXT_GRAY, leading=9,  spaceAfter=1),
        "card_value": base("card_value", fontName="Helvetica-Bold",   fontSize=11, textColor=DARK,      leading=14),
        "body":       base("body",       fontName="Helvetica",        fontSize=9,  textColor=DARK,      leading=13),
        "cite":       base("cite",       fontName="Helvetica-Oblique",fontSize=8,  textColor=TEXT_GRAY, leading=11),
        "metric_val": base("metric_val", fontName="Helvetica-Bold",   fontSize=20, textColor=PRIMARY,   leading=24, alignment=TA_CENTER),
        "metric_lbl": base("metric_lbl", fontName="Helvetica",        fontSize=7,  textColor=TEXT_GRAY, leading=9,  alignment=TA_CENTER),
        "motif_name": base("motif_name", fontName="Helvetica-Bold",   fontSize=10, textColor=DARK,      leading=13),
        "motif_conf": base("motif_conf", fontName="Helvetica",        fontSize=8,  textColor=PRIMARY,   leading=10),
        "footer":     base("footer",     fontName="Helvetica",        fontSize=7,  textColor=TEXT_GRAY, leading=9,  alignment=TA_CENTER),
        "alert":      base("alert",      fontName="Helvetica-Bold",   fontSize=9,  textColor=colors.HexColor("#7d4c00"), leading=12),
    }


def _section_header(title: str, ST: dict) -> list:
    """Devuelve [spacer, label, línea]."""
    return [
        Spacer(1, 5 * mm),
        Paragraph(title.upper(), ST["section"]),
        HRFlowable(width="100%", thickness=1, color=MID_GRAY, spaceAfter=4),
    ]


def _card_table(pairs: list[tuple[str, str]], ST: dict, cols: int = 2) -> Table:
    """Genera tabla de tarjetas tipo card-grid."""
    cell_w = (W - 2 * MARGIN) / cols
    rows = []
    for i in range(0, len(pairs), cols):
        row = []
        for label, value in pairs[i:i + cols]:
            cell = [
                Paragraph(label, ST["card_label"]),
                Paragraph(str(value), ST["card_value"]),
            ]
            row.append(cell)
        # rellenar si la fila está incompleta
        while len(row) < cols:
            row.append("")
        rows.append(row)

    t = Table(rows, colWidths=[cell_w] * cols, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX",          (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, WHITE),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _confidence_bar(confidence: float, width: float = 80) -> Table:
    """Barra visual de confianza (roja como en el diseño)."""
    pct = max(0.0, min(1.0, confidence))
    filled = width * pct
    empty  = width - filled
    bar = Table(
        [["", ""]],
        colWidths=[filled, empty] if empty > 0 else [width, 0.001],
        rowHeights=[4],
    )
    bar.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), PRIMARY),
        ("BACKGROUND",    (1, 0), (1, 0), MID_GRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    return bar


def _motifs_grid(motifs: list[dict], ST: dict) -> Table:
    """Grid de tarjetas de motivos con barra de confianza."""
    cols = 4
    cell_w = (W - 2 * MARGIN) / cols
    rows = []
    for i in range(0, len(motifs), cols):
        row_data = []
        for m in motifs[i:i + cols]:
            conf  = m.get("confidence", 0.0)
            clase = m.get("clase", "Desconocido").replace("_", " ").title()
            cell  = [
                Paragraph("MOTIVO", ST["card_label"]),
                Paragraph(clase, ST["motif_name"]),
                Spacer(1, 2),
                _confidence_bar(conf, cell_w - 22),
                Spacer(1, 2),
                Paragraph(f"{conf*100:.0f}% conf.", ST["motif_conf"]),
            ]
            row_data.append(cell)
        while len(row_data) < cols:
            row_data.append("")
        rows.append(row_data)

    t = Table(rows, colWidths=[cell_w] * cols, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _parallels_table(similar_motifs: list[dict], ST: dict) -> Table:
    """Lista de paralelos con score a la derecha."""
    all_matches = []
    for sm in similar_motifs:
        for match in sm.get("top_matches", []):
            all_matches.append(match)

    if not all_matches:
        return Paragraph("No se encontraron paralelos iconográficos regionales.", ST["body"])

    col_w = W - 2 * MARGIN
    rows = []
    for m in all_matches:
        site    = m.get("site", "Desconocido")
        cultura = m.get("cultura", "")
        periodo = m.get("periodo", "")
        score   = m.get("score", 0.0)

        left  = [
            Paragraph(f"<b>{site}</b>", ST["body"]),
            Paragraph(f"{cultura} · {periodo}", ST["cite"]),
        ]
        right = Paragraph(f"<b>{score:.2f}</b>", ParagraphStyle(
            "score", fontName="Helvetica-Bold", fontSize=12,
            textColor=TEAL, alignment=TA_RIGHT
        ))
        rows.append([left, right])

    t = Table(rows, colWidths=[col_w * 0.80, col_w * 0.20], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.5, WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _metrics_row(motif_count: int, confidence: float,
                 n_parallels: int, ST: dict) -> Table:
    """Fila de métricas técnicas al estilo del diseño."""
    col_w = (W - 2 * MARGIN) / 4

    def metric_cell(value: str, label: str) -> list:
        return [
            Paragraph(value, ST["metric_val"]),
            Paragraph(label, ST["metric_lbl"]),
        ]

    row = [
        metric_cell(str(motif_count),         "MOTIVOS\nDETECTADOS"),
        metric_cell(f"{confidence:.2f}",      "CONFIANZA\nRAG"),
        metric_cell(str(n_parallels),         "PARALELOS\nREGIONALES"),
        metric_cell("< 45 min",               "TIEMPO DE\nANÁLISIS"),
    ]
    t = Table([row], colWidths=[col_w] * 4, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, WHITE),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


# ── Función principal ──────────────────────────────────────────────────────────
def generate_pdf(ficha: dict, output_path: str) -> str:
    """
    Genera la ficha ICANH en PDF profesional.

    Args:
        ficha: dict con todos los campos de FichaICANH
        output_path: ruta destino del PDF
    Returns:
        output_path
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ST = _styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title="Ficha de Registro Rupestre ICANH",
        author="Rupestre AI — UPTC 2026",
    )

    # Datos del estado
    record_id    = ficha.get("record_id", "N/A")
    site_name    = ficha.get("site_name", "Sin nombre")
    coords       = ficha.get("coordinates", (0.0, 0.0))
    dept         = ficha.get("department", "No especificado")
    municipality = ficha.get("municipality", "No especificado")
    motif_count  = ficha.get("motif_count", 0)
    motifs       = ficha.get("detected_motifs", [])
    similar      = ficha.get("similar_motifs", [])
    has_parallels= ficha.get("has_regional_parallels", False)
    interp       = ficha.get("cultural_interpretation", "")
    sources      = ficha.get("cited_sources", [])
    confidence   = ficha.get("interpretation_confidence", 0.0)
    recon        = ficha.get("reconstruction_applied", False)
    now_str      = datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M UTC")

    # Contar paralelos totales
    n_parallels = sum(len(sm.get("top_matches", [])) for sm in similar)

    story = []

    # ── ENCABEZADO ────────────────────────────────────────────────────────────
    header_data = [[
        [
            Paragraph("Ficha de Registro ICANH", ST["title"]),
            Paragraph("Sistema Rupestre AI · UPTC 2026", ST["subtitle"]),
        ],
        [
            Paragraph(f"<b>ID</b>  {record_id}", ST["body"]),
            Paragraph(now_str, ST["subtitle"]),
        ],
    ]]
    header_table = Table(
        header_data,
        colWidths=[(W - 2 * MARGIN) * 0.65, (W - 2 * MARGIN) * 0.35],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (1, 0),   "RIGHT"),
    ]))
    # Forzar color de texto blanco en el header
    for s in [ST["title"], ST["subtitle"], ST["body"]]:
        s.textColor = WHITE
    story.append(header_table)

    # Restaurar colores para el resto del documento
    ST = _styles()

    # ── BANNER DE ALERTA (si hay paralelos) ──────────────────────────────────
    if has_parallels:
        alert_text = (f"● Paralelos iconográficos regionales encontrados — "
                      f"<b>{n_parallels} sitios</b> con similitud > 0.80")
        alert_table = Table(
            [[Paragraph(alert_text, ST["alert"])]],
            colWidths=[W - 2 * MARGIN],
        )
        alert_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#fff3cd")),
            ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#f0ad4e")),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ]))
        story.append(Spacer(1, 4 * mm))
        story.append(alert_table)

    # ── IDENTIFICACIÓN DEL SITIO ──────────────────────────────────────────────
    story += _section_header("Identificación del sitio", ST)
    coord_str = f"{coords[0]:.3f}°N,  {coords[1]:.3f}°W"
    story.append(_card_table([
        ("SITIO RUPESTRE",       site_name),
        ("DEPARTAMENTO",         dept),
        ("COORDENADAS GPS",      coord_str),
        ("MUNICIPIO",            municipality),
    ], ST, cols=2))

    # ── GALERÍA DE IMÁGENES ───────────────────────────────────────────────────
    story += _section_header("Galería de imágenes", ST)
    images_info = ficha.get("images", {})
    gallery_labels = [
        ("Original\ncaptura de campo", images_info.get("original", "N/A")),
        ("Realzada\nDStretch-LAB",      images_info.get("enhanced", "N/A")),
        ("Reconstruida\nDeepFillv2",    images_info.get("reconstructed", "N/A")),
    ]
    col_w = (W - 2 * MARGIN) / 3

    # Intentar cargar imágenes reales
    from reportlab.platypus import Image as RLImage

    gallery_cells = []
    for label, img_path in gallery_labels:
        cell_content = []
        loaded = False
        if img_path and img_path != "N/A" and os.path.exists(str(img_path)):
            try:
                img = RLImage(str(img_path), width=col_w - 6, height=40 * mm)
                cell_content.append(img)
                loaded = True
            except Exception:
                pass
        if not loaded:
            placeholder = Table(
                [[Paragraph("PICTOGRAFÍA", ParagraphStyle(
                    "ph", fontName="Helvetica", fontSize=8,
                    textColor=TEXT_GRAY, alignment=TA_CENTER))]],
                colWidths=[col_w - 6], rowHeights=[40 * mm],
            )
            placeholder.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), MID_GRAY),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ]))
            cell_content.append(placeholder)

        cell_content.append(Spacer(1, 2))
        cell_content.append(Paragraph(label, ParagraphStyle(
            "img_lbl", fontName="Helvetica", fontSize=7,
            textColor=TEXT_GRAY, alignment=TA_CENTER, leading=9
        )))
        gallery_cells.append(cell_content)

    gallery_table = Table(
        [gallery_cells], colWidths=[col_w] * 3, hAlign="LEFT"
    )
    gallery_table.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 3),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 3),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(gallery_table)

    # ── MOTIVOS DETECTADOS ────────────────────────────────────────────────────
    story += _section_header(f"Motivos detectados — {motif_count} elementos", ST)
    if motifs:
        story.append(_motifs_grid(motifs, ST))
    else:
        story.append(Paragraph("No se detectaron motivos.", ST["body"]))

    # ── PARALELOS ICONOGRÁFICOS ───────────────────────────────────────────────
    story += _section_header("Paralelos iconográficos regionales", ST)
    story.append(_parallels_table(similar, ST))

    # ── INTERPRETACIÓN CULTURAL ───────────────────────────────────────────────
    story += _section_header("Interpretación cultural", ST)

    interp_safe = interp.encode("latin-1", "replace").decode("latin-1")
    interp_table = Table(
        [[Paragraph(interp_safe, ST["body"])]],
        colWidths=[W - 2 * MARGIN],
    )
    interp_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), WARM_BG),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#f0d9a0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    story.append(interp_table)

    # Fuentes citadas
    if sources:
        story.append(Spacer(1, 3 * mm))
        for src in sources:
            author = src.get("author", "")
            year   = src.get("year", "")
            title  = src.get("title", "")
            txt    = f"■  {author} ({year}). <i>{title}</i>."
            txt_safe = txt.encode("latin-1", "replace").decode("latin-1")
            story.append(Paragraph(txt_safe, ST["cite"]))
            story.append(Spacer(1, 1 * mm))

    # ── MÉTRICAS TÉCNICAS ─────────────────────────────────────────────────────
    story += _section_header("Métricas técnicas del análisis", ST)
    story.append(_metrics_row(motif_count, confidence, n_parallels, ST))

    # ── PIE DE PÁGINA ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 2 * mm))
    footer_data = [[
        Paragraph("Rupestre AI · UPTC · En coordinación con el ICANH", ST["footer"]),
        Paragraph(f"ID: {record_id} · v1.0.0", ST["footer"]),
    ]]
    footer_table = Table(
        footer_data,
        colWidths=[(W - 2 * MARGIN) * 0.6, (W - 2 * MARGIN) * 0.4],
    )
    footer_table.setStyle(TableStyle([
        ("ALIGN",  (1, 0), (1, 0), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(footer_table)

    doc.build(story)
    return output_path