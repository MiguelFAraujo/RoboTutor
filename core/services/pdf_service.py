from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from core.catalog import PDF_OUTPUT_DIR, PROJECT_PACKS, get_pack_by_slug, get_pack_pdf_path


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="PackTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=colors.HexColor("#0f172a"),
            alignment=TA_LEFT,
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PackSubhead",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f766e"),
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyTight",
            parent=styles["BodyText"],
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor("#1f2937"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#475569"),
            spaceAfter=6,
        )
    )
    return styles


def bullet_list(items, styles):
    return ListFlowable(
        [ListItem(Paragraph(str(item), styles["BodyTight"])) for item in items],
        bulletType="bullet",
        leftIndent=14,
    )


def project_table(project, styles):
    rows = [
        ["Projeto", project["name"]],
        ["Problema que resolve", project["problem"]],
        ["Materiais", ", ".join(project["bill_of_materials"])],
    ]
    table = Table(rows, colWidths=[4.2 * cm, 11.8 * cm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#dbeafe")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#93c5fd")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def build_pack_story(pack):
    styles = build_styles()
    story = []

    story.append(Paragraph(pack["title"], styles["PackTitle"]))
    story.append(Paragraph(pack["hook"], styles["BodyTight"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(f"<b>Plataforma:</b> {pack['platform']}", styles["Meta"]))
    story.append(Paragraph(f"<b>Publico:</b> {pack['audience']}", styles["Meta"]))
    story.append(Paragraph(f"<b>Formato ideal:</b> {pack['offer_type']}", styles["Meta"]))
    story.append(Paragraph(f"<b>Faixa comercial:</b> {pack['price_anchor']}", styles["Meta"]))
    story.append(Paragraph(f"<b>Dificuldade:</b> {pack['difficulty']} | <b>Duracao:</b> {pack['duration']}", styles["Meta"]))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Resultados Prometidos", styles["PackSubhead"]))
    story.append(bullet_list(pack["outcomes"], styles))

    story.append(Paragraph("Angulos de Venda", styles["PackSubhead"]))
    story.append(bullet_list(pack["sales_angles"], styles))

    story.append(Paragraph("Estrutura dos Projetos", styles["PackSubhead"]))
    for project in pack["projects"]:
        story.append(project_table(project, styles))
        story.append(Spacer(1, 0.15 * cm))
        story.append(Paragraph("<b>Passo a passo do PDF</b>", styles["Meta"]))
        story.append(bullet_list(project["steps"], styles))
        story.append(Paragraph("<b>Upsells e extensoes</b>", styles["Meta"]))
        story.append(bullet_list(project["extensions"], styles))
        story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Checklist de publicacao", styles["PackSubhead"]))
    story.append(
        bullet_list(
            [
                "Fotografar cada projeto finalizado e incluir uma pagina com portfolio visual.",
                "Adicionar link para repositorio ou codigo complementar.",
                "Oferecer bonus: lista de compras, rubrica de avaliacao ou desafio extra.",
                "Usar este PDF como produto de entrada para assinatura, oficina ou mentoria.",
            ],
            styles,
        )
    )

    return story


def generate_pack_pdf(pack, output_path=None):
    output_path = Path(output_path or get_pack_pdf_path(pack["slug"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1.6 * cm,
        rightMargin=1.6 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=pack["title"],
        author="RoboTutor",
    )
    doc.build(build_pack_story(pack))
    return output_path


def generate_catalog_bundle(output_dir=None):
    output_dir = Path(output_dir or PDF_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    created_files = []
    for pack in PROJECT_PACKS:
        created_files.append(generate_pack_pdf(pack, output_dir / f"{pack['slug']}.pdf"))
    return created_files


def generate_single_pack(slug, output_dir=None):
    pack = get_pack_by_slug(slug)
    if not pack:
        raise ValueError(f"Pack desconhecido: {slug}")
    output_dir = Path(output_dir or PDF_OUTPUT_DIR)
    return generate_pack_pdf(pack, output_dir / f"{slug}.pdf")
