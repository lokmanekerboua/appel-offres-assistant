import logging
from datetime import datetime, timezone
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

logger = logging.getLogger(__name__)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=18, spaceAfter=16)
heading_style = ParagraphStyle("CustomHeading", parent=styles["Heading2"], fontSize=13, spaceBefore=16, spaceAfter=8)
body_style = ParagraphStyle("CustomBody", parent=styles["Normal"], fontSize=10, leading=15)


def generate_analysis_pdf(tender_text: str, analysis: dict) -> bytes:
    """
    Builds a structured PDF report from a tender analysis result.
    Returns raw PDF bytes, ready to upload to S3 or return as a file.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
    )
    story = []

    story.append(Paragraph("Rapport d'analyse d'appel d'offres", title_style))
    story.append(Paragraph(
        f"Généré le {datetime.now(timezone.utc):%d/%m/%Y à %H:%M} UTC",
        ParagraphStyle("Subtitle", parent=styles["Normal"], textColor=colors.grey, fontSize=9),
    ))
    story.append(Spacer(1, 12))

    # --- Requirements ---
    story.append(Paragraph("Exigences extraites", heading_style))
    req = analysis.get("requirements", {})
    req_rows = [
        ["Deadline", req.get("deadline") or "Non précisé"],
        ["Budget", req.get("budget") or "Non précisé"],
        ["Certifications requises", ", ".join(req.get("required_certifications", [])) or "Aucune"],
        ["Livrables", ", ".join(req.get("deliverables", [])) or "Non précisé"],
        ["Mots-clés", ", ".join(req.get("keywords", [])) or "Aucun"],
    ]
    req_table = Table(req_rows, colWidths=[4 * cm, 12 * cm])
    req_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(req_table)

    # --- Eligibility ---
    story.append(Paragraph("Éligibilité", heading_style))
    elig = analysis.get("eligibility", {})
    is_eligible = elig.get("is_eligible", False)
    verdict_color = colors.HexColor("#2e7d32") if is_eligible else colors.HexColor("#c62828")
    verdict_text = "ÉLIGIBLE" if is_eligible else "NON ÉLIGIBLE"
    story.append(Paragraph(
        f'<font color="{verdict_color.hexval()}"><b>{verdict_text}</b></font>',
        body_style,
    ))
    missing = elig.get("missing_certifications", [])
    if missing:
        story.append(Paragraph(f"Certifications/critères manquants : {', '.join(missing)}", body_style))
    for note in elig.get("risk_notes", []):
        story.append(Paragraph(f"• {note}", body_style))

    # --- References ---
    story.append(Paragraph("Références correspondantes", heading_style))
    matched = analysis.get("matched_references", [])
    if matched:
        ref_rows = [["Projet", "Client", "Pertinence"]]
        for ref in matched:
            ref_rows.append([
                ref.get("project_name", ""),
                ref.get("client", ""),
                f"{ref.get('relevance_score', 0):.0%}",
            ])
        ref_table = Table(ref_rows, colWidths=[7 * cm, 6 * cm, 3 * cm])
        ref_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(ref_table)
    else:
        story.append(Paragraph("Aucune référence pertinente trouvée.", body_style))

    # --- Draft intro ---
    story.append(Paragraph("Introduction proposée pour la réponse", heading_style))
    story.append(Paragraph(analysis.get("draft_intro", ""), body_style))

    # --- Original tender text (appendix) ---
    story.append(Spacer(1, 20))
    story.append(Paragraph("Annexe : texte source de l'appel d'offres", heading_style))
    story.append(Paragraph(tender_text.replace("\n", "<br/>"), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()