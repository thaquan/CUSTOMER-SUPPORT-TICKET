"""Build the portfolio case-study PDF and keep its layout reproducible."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = (
    PROJECT_ROOT
    / "output"
    / "pdf"
    / "customer-support-analytics-case-study.pdf"
)
IMAGE_DIR = PROJECT_ROOT / "powerbi" / "img"

PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)

PURPLE = colors.HexColor("#5138EE")
DARK_PURPLE = colors.HexColor("#3C2AA8")
LIGHT_PURPLE = colors.HexColor("#F1EEFF")
NAVY = colors.HexColor("#1D2140")
MUTED = colors.HexColor("#6F748C")
GREEN = colors.HexColor("#20B486")
ORANGE = colors.HexColor("#F4A340")
RED = colors.HexColor("#EB5757")
LINE = colors.HexColor("#DCDDEA")
CANVAS = colors.HexColor("#F7F7FC")
WHITE = colors.white


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=27,
        leading=31,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverSubtitle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=MUTED,
        spaceAfter=10,
    )
)
styles.add(
    ParagraphStyle(
        name="SectionTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=NAVY,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="SectionIntro",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=MUTED,
        spaceAfter=9,
    )
)
styles.add(
    ParagraphStyle(
        name="CardTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=13,
        textColor=NAVY,
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        name="TableHeader",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=WHITE,
    )
)
styles.add(
    ParagraphStyle(
        name="BodySmall",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.4,
        leading=12,
        textColor=NAVY,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyTiny",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.4,
        leading=10,
        textColor=NAVY,
    )
)
styles.add(
    ParagraphStyle(
        name="MetricValue",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=19,
        textColor=PURPLE,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="MetricLabel",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="GalleryTitle",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=NAVY,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="Callout",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=DARK_PURPLE,
        alignment=TA_CENTER,
    )
)


def page_chrome(canvas, doc):
    """Draw a restrained header/footer on every page."""
    canvas.saveState()
    canvas.setFillColor(CANVAS)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.setFillColor(PURPLE)
    canvas.rect(0, PAGE_HEIGHT - 5 * mm, PAGE_WIDTH, 5 * mm, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(DARK_PURPLE)
    canvas.drawString(14 * mm, 8 * mm, "CUSTOMER SUPPORT ANALYTICS")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(
        PAGE_WIDTH - 14 * mm,
        8 * mm,
        f"Portfolio case study  |  Page {doc.page}",
    )
    canvas.restoreState()


def make_image(filename, width, height):
    path = IMAGE_DIR / filename
    image = Image(str(path), width=width, height=height)
    image.hAlign = "CENTER"
    return image


def metric_card(value, label, color=PURPLE):
    value_style = ParagraphStyle(
        name=f"Metric-{value}",
        parent=styles["MetricValue"],
        textColor=color,
    )
    return Table(
        [[Paragraph(value, value_style)], [Paragraph(label, styles["MetricLabel"])]],
        colWidths=[43 * mm],
        rowHeights=[11 * mm, 9 * mm],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        ),
    )


def content_card(title, body, width=84 * mm, background=WHITE):
    return Table(
        [[Paragraph(title, styles["CardTitle"])], [Paragraph(body, styles["BodySmall"])]],
        colWidths=[width],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        ),
    )


def build_story():
    story = []

    # Page 1 - Cover
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("Customer Support Analytics", styles["CoverTitle"]))
    story.append(
        Paragraph(
            "From 8,469 raw tickets to a validated SQL Server star schema and a five-page Power BI decision-support report.",
            styles["CoverSubtitle"],
        )
    )
    story.append(
        Table(
            [[
                metric_card("8,469", "support tickets"),
                metric_card("67.30%", "backlog rate", RED),
                metric_card("35", "DAX measures"),
                metric_card("21 / 21", "Python tests", GREEN),
                metric_card("5", "report pages", ORANGE),
            ]],
            colWidths=[47 * mm] * 5,
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
        )
    )
    story.append(Spacer(1, 7 * mm))
    story.append(make_image("page1-executive-overview.png", 200 * mm, 116 * mm))
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "Python  |  pandas  |  SQL Server  |  Dimensional Modeling  |  DAX  |  Power BI  |  Git",
            styles["Callout"],
        )
    )
    story.append(PageBreak())

    # Page 2 - Problem, architecture, model
    story.append(Paragraph("Business problem and delivery architecture", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "A simulated Customer Experience team needs a reliable view of unresolved workload, service demand, satisfaction, resolution performance, and customer segments. The solution separates data engineering from analytical modeling so that quality failures remain auditable.",
            styles["SectionIntro"],
        )
    )
    steps = [
        ("BRONZE", "Immutable local Kaggle CSV"),
        ("SILVER", "Python cleaning, flags, pseudonymization"),
        ("GOLD", "FactTicket plus seven dimensions"),
        ("SQL", "Staging, typed analytics, 34 checks"),
        ("POWER BI", "35 DAX measures and five pages"),
    ]
    step_cells = []
    for title, body in steps:
        step_cells.append(
            Table(
                [[Paragraph(title, styles["TableHeader"])], [Paragraph(body, styles["BodyTiny"])]],
                colWidths=[43 * mm],
                rowHeights=[8 * mm, 15 * mm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
                        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                        ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ]
                ),
            )
        )
    story.append(
        Table(
            [step_cells],
            colWidths=[47 * mm] * 5,
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
        )
    )
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph("Analytical model", styles["SectionTitle"]))
    model_data = [
        [Paragraph("Component", styles["TableHeader"]), Paragraph("Design", styles["TableHeader"]), Paragraph("Reason", styles["TableHeader"])],
        ["FactTicket", "One row per validated ticket; 21 fields", "Stable business grain and additive ticket counts"],
        ["7 dimensions", "Customer profile, product, issue, channel, priority, status, purchase date", "Reusable filtering and controlled dimension grain"],
        ["7 relationships", "Many-to-one, fact-to-dimension", "Predictable filter propagation and simpler DAX"],
        ["_Measures", "35 explicit measures in business folders", "Governed definitions and consistent formatting"],
        ["Privacy", "Names and emails excluded from public model", "Portfolio-safe demographic analysis"],
    ]
    model_table = Table(model_data, colWidths=[38 * mm, 92 * mm, 105 * mm], repeatRows=1)
    model_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK_PURPLE),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_PURPLE]),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(model_table)
    story.append(Spacer(1, 7 * mm))
    story.append(
        Table(
            [[
                content_card("Why a star schema?", "It makes ticket grain, filter propagation, dimension uniqueness, and foreign-key reconciliation explicit.", 74 * mm),
                content_card("Why Import mode?", "The portfolio dataset is static and small enough for fast interactive analysis without DirectQuery complexity.", 74 * mm),
                content_card("Why purchase cohorts?", "Purchase date is available, but ticket-created date is not. The report avoids presenting a false ticket-arrival trend.", 74 * mm),
            ]],
            colWidths=[79 * mm] * 3,
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
        )
    )
    story.append(PageBreak())

    # Page 3 - Findings and integrity
    story.append(Paragraph("Findings with analytical integrity", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "The dashboard highlights operational risk while making denominator, sample, and source constraints visible.",
            styles["SectionIntro"],
        )
    )
    findings = [
        ("Workload", "5,700 tickets are unresolved; the backlog rate is 67.30%. Critical/High backlog contains 783 tickets."),
        ("Customer experience", "2,769 tickets have CSAT. Average CSAT is 2.99 and 39.80% of respondents rated service 1 or 2."),
        ("Resolution cycle", "1,404 records have a valid first-response-to-resolution cycle. Median is 380.50 minutes; average is 454.68."),
        ("Channel", "Email has the highest observed volume at 2,143 tickets. Chat has the highest observed average CSAT at 3.08."),
        ("Issue demand", "Refund Request / Hardware issue is the largest observed issue combination with 129 tickets."),
        ("Product context", "Canon EOS has the highest observed ticket volume at 240, but sales volume is unavailable, so this is not a defect rate."),
    ]
    cards = [content_card(title, body, 72 * mm) for title, body in findings]
    story.append(
        Table(
            [cards[:3], cards[3:]],
            colWidths=[78 * mm] * 3,
            rowHeights=[33 * mm, 33 * mm],
            style=TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            ),
        )
    )
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph("Quality evidence", styles["SectionTitle"]))
    quality_data = [
        ["Check", "Result", "Interpretation"],
        ["Raw / Silver / Fact rows", "8,469 / 8,469 / 8,469", "Complete row reconciliation"],
        ["Duplicate ticket IDs", "0", "Fact grain preserved"],
        ["Missing Gold foreign keys", "0", "All relationships resolve"],
        ["Invalid parsed values", "0", "Age, CSAT, date, and timestamp parsing passed"],
        ["Negative temporal cycles", "1,365 (16.12%)", "Flagged and excluded from duration KPIs"],
        ["Automated validation", "21 Python tests + 34 SQL checks", "Repeatable quality gates"],
    ]
    quality_table = Table(quality_data, colWidths=[58 * mm, 52 * mm, 125 * mm], repeatRows=1)
    quality_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK_PURPLE),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_PURPLE]),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(quality_table)
    story.append(Spacer(1, 8 * mm))
    story.append(
        Table(
            [[Paragraph(
                "A negative duration is evidence of a source-quality problem, not a number that should be repaired with abs(). The project preserves a quality flag and leaves the analytical duration blank.",
                styles["Callout"],
            )]],
            colWidths=[235 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_PURPLE),
                    ("BOX", (0, 0), (-1, -1), 1, PURPLE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ]
            ),
        )
    )
    story.append(PageBreak())

    # Page 4 - Dashboard gallery
    story.append(Paragraph("Power BI report gallery", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "Five pages separate executive monitoring, operations, customer experience, resolution quality, and customer segmentation. The Executive Overview appears on the cover; the remaining pages are shown below.",
            styles["SectionIntro"],
        )
    )
    gallery_specs = [
        ("Support Operations", "page2-support-operations.png"),
        ("Customer Experience & CSAT", "page3-customer-experience.png"),
        ("Resolution Performance", "page4-resolution-quality.png"),
        ("Customer Segments", "page5-customer-segments.png"),
    ]
    gallery_cells = []
    for title, filename in gallery_specs:
        gallery_cells.append(
            [
                Paragraph(title, styles["GalleryTitle"]),
                Spacer(1, 2 * mm),
                make_image(filename, 101 * mm, 58.6 * mm),
            ]
        )
    story.append(
        Table(
            [gallery_cells[:2], gallery_cells[2:]],
            colWidths=[118 * mm, 118 * mm],
            rowHeights=[70 * mm, 70 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            ),
        )
    )
    story.append(Spacer(1, 5 * mm))
    story.append(
        Paragraph(
            "UX controls: consistent page navigation, labeled slicers, sample-size context, explanatory caveats, visual alt text, and deterministic tab order.",
            styles["Callout"],
        )
    )
    story.append(PageBreak())

    # Page 5 - Recommendations and close
    story.append(Paragraph("Recommendations, limitations, and outcome", styles["SectionTitle"]))
    story.append(Spacer(1, 2 * mm))
    recommendations = [
        ("1. Prioritize urgency", "Review the 783 Critical/High unresolved tickets and monitor their share of backlog."),
        ("2. Improve survey coverage", "A 32.70% response rate limits how confidently CSAT findings generalize to all tickets."),
        ("3. Investigate segments", "Use subject, channel, and product rates to select cases for qualitative review, not to claim causation."),
        ("4. Repair event capture", "Add ticket-created timestamps and prevent resolution events from preceding first response."),
        ("5. Add denominators", "Capture sales volume, SLA targets, agent capacity, order value, and support cost."),
    ]
    recommendation_cards = [content_card(t, b, 44 * mm, LIGHT_PURPLE) for t, b in recommendations]
    story.append(
        Table(
            [recommendation_cards],
            colWidths=[47 * mm] * 5,
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
        )
    )
    story.append(Spacer(1, 8 * mm))
    left = content_card(
        "Known limitations",
        "- No explicit ticket-created timestamp.<br/>- Purchase date is not ticket-arrival date.<br/>- CSAT covers respondents only.<br/>- Resolution cycle starts at first response.<br/>- No agent, SLA, sales, revenue, or cost fields.<br/>- Segment comparisons are descriptive, not causal.",
        111 * mm,
    )
    right = content_card(
        "Portfolio evidence",
        "- Source-controlled PBIP definitions.<br/>- 21 Python tests and 34 SQL checks.<br/>- Versioned Silver and Gold quality summaries.<br/>- 35 explicit DAX measures.<br/>- Five verified report screenshots.<br/>- Private Power BI Service deployment.",
        111 * mm,
    )
    story.append(
        Table(
            [[left, right]],
            colWidths=[118 * mm, 118 * mm],
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
        )
    )
    story.append(Spacer(1, 9 * mm))
    story.append(
        Table(
            [[Paragraph(
                "Outcome: a reproducible analytical product that combines engineering, modeling, validation, dashboard design, deployment, and transparent communication of uncertainty.",
                styles["Callout"],
            )]],
            colWidths=[235 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                    ("BOX", (0, 0), (-1, -1), 1.2, PURPLE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            ),
        )
    )
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Repository", styles["CardTitle"]))
    story.append(
        Paragraph(
            "https://github.com/thaquan/CUSTOMER-SUPPORT-TICKET",
            styles["BodySmall"],
        )
    )
    story.append(Paragraph("Dataset", styles["CardTitle"]))
    story.append(
        Paragraph(
            "Customer Support Ticket Dataset by Suraj on Kaggle, CC0 - Public Domain.",
            styles["BodySmall"],
        )
    )
    return story


def build_pdf():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    frame = Frame(
        14 * mm,
        14 * mm,
        PAGE_WIDTH - 28 * mm,
        PAGE_HEIGHT - 25 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    doc = BaseDocTemplate(
        str(OUTPUT_FILE),
        pagesize=landscape(A4),
        title="Customer Support Analytics - Portfolio Case Study",
        author="thaquan",
        subject="End-to-end Python, SQL Server, DAX, and Power BI portfolio project",
        creator="ReportLab",
    )
    doc.addPageTemplates([PageTemplate(id="portfolio", frames=[frame], onPage=page_chrome)])
    doc.build(build_story())
    print(OUTPUT_FILE)


if __name__ == "__main__":
    build_pdf()
