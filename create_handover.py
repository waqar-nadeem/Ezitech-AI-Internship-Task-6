#!/usr/bin/env python3
"""Generate the one-page HandOver_Mehfil.pdf for Task 6."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUTPUT = "HandOver_Mehfil.pdf"

def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontSize=14,
        leading=17,
        textColor=HexColor("#1a365d"),
        alignment=TA_CENTER,
        spaceAfter=2,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="SubTitle",
        fontSize=9,
        leading=11,
        textColor=HexColor("#2d3748"),
        alignment=TA_CENTER,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="SectionHead",
        fontSize=10,
        leading=12,
        textColor=HexColor("#2b6cb0"),
        spaceBefore=7,
        spaceAfter=2,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="Body",
        fontSize=8.5,
        leading=10.5,
        textColor=HexColor("#1a202c"),
        alignment=TA_JUSTIFY,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="BulletItem",
        fontSize=8.5,
        leading=10.5,
        leftIndent=8,
        textColor=HexColor("#1a202c"),
        spaceAfter=1,
    ))
    styles.add(ParagraphStyle(
        name="Footer",
        fontSize=7,
        textColor=HexColor("#718096"),
        alignment=TA_CENTER,
        spaceBefore=4,
    ))
    styles.add(ParagraphStyle(
        name="Meta",
        fontSize=8,
        leading=10,
        textColor=HexColor("#4a5568"),
        alignment=TA_CENTER,
        spaceAfter=4,
    ))

    story = []

    # Header
    story.append(Paragraph(
        "Hand-Over Document – AI-Powered Meeting Transcript Summariser",
        styles["DocTitle"],
    ))
    story.append(Paragraph(
        "Mehfil Event Planners &nbsp;|&nbsp; Ezitech AI Internship (Task 6) &nbsp;|&nbsp; Intern: Waqar Nadeem",
        styles["SubTitle"],
    ))
    story.append(HRFlowable(width="100%", thickness=1.2, color=HexColor("#2b6cb0"), spaceAfter=4))

    # Project overview
    story.append(Paragraph("1. Project Overview", styles["SectionHead"]))
    story.append(Paragraph(
        "Mehfil Event Planners coordinates dozens of vendor and client meetings for weddings and events. "
        "This web tool lets users upload a meeting transcript (or paste text), automatically generates a clear "
        "executive summary with key decisions and action items, runs a simple quality checklist, and produces "
        "a downloadable Markdown / PDF report — removing the need for manual note-taking.",
        styles["Body"],
    ))

    # Architecture
    story.append(Paragraph("2. Architecture & Tech Stack", styles["SectionHead"]))
    story.append(Paragraph(
        "<b>Frontend / App:</b> Streamlit (single-file app.py) &nbsp;•&nbsp; "
        "<b>Model:</b> Open-source DistilBART (sshleifer/distilbart-cnn-12-6) via Hugging Face Transformers &nbsp;•&nbsp; "
        "<b>Chunking:</b> Sentence-aware splitting (~450 words) with light overlap &nbsp;•&nbsp; "
        "<b>Decision / Action extraction:</b> Lightweight rule-based patterns (no second LLM call) &nbsp;•&nbsp; "
        "<b>PDF:</b> ReportLab &nbsp;•&nbsp; "
        "<b>Parsers:</b> pypdf + python-docx &nbsp;•&nbsp; "
        "<b>Deployment:</b> Streamlit Community Cloud (CPU-only free tier).",
        styles["Body"],
    ))

    # How to use
    story.append(Paragraph("3. How to Use", styles["SectionHead"]))
    story.append(Paragraph("• Upload a .txt / .pdf / .docx transcript or paste text directly.", styles["BulletItem"]))
    story.append(Paragraph("• Click <b>Generate Summary & Report</b>. Long transcripts are automatically chunked.", styles["BulletItem"]))
    story.append(Paragraph("• Review the executive summary, extracted key decisions, action items and quality checklist.", styles["BulletItem"]))
    story.append(Paragraph("• Download the report as Markdown or PDF for sharing with the client / internal team.", styles["BulletItem"]))
    story.append(Paragraph("• Sample file: <font face='Courier'>sample_data/sample_transcript.txt</font>", styles["BulletItem"]))

    # Local & Cloud
    story.append(Paragraph("4. Local Setup & Cloud Deployment", styles["SectionHead"]))
    story.append(Paragraph(
        "<b>Local:</b> <font face='Courier'>pip install -r requirements.txt && streamlit run app.py</font><br/>"
        "<b>Cloud:</b> Push repo to GitHub → share.streamlit.io → New app → select repo / main / app.py → Deploy. "
        "First run downloads model weights (~300 MB); later runs use Streamlit resource cache.",
        styles["Body"],
    ))

    # Limitations
    story.append(Paragraph("5. Limitations & Recommendations", styles["SectionHead"]))
    story.append(Paragraph(
        "• DistilBART is efficient but can miss subtle or implied decisions; always verify critical items against the original transcript.<br/>"
        "• Action-item extraction is rule-based for speed and free-tier reliability; complex ownership language may need manual review.<br/>"
        "• Very long meetings (> ~8 000 words) are multi-chunked; a merge pass is applied but some fine detail can still be lost.<br/>"
        "• Recommended next steps: add speaker diarisation, optional LLM re-ranking of action items, and user login for history.",
        styles["Body"],
    ))

    # Deliverables
    story.append(Paragraph("6. Deliverables Checklist", styles["SectionHead"]))
    data = [
        ["Item", "Status"],
        ["GitHub repository with full source", "✓"],
        ["Streamlit web app (Community Cloud)", "✓ (update URL in README)"],
        ["README with badge, setup, usage, deployment link", "✓"],
        ["Sample transcript + generated summary flow", "✓"],
        ["This one-page HandOver_Mehfil.pdf", "✓"],
    ]
    t = Table(data, colWidths=[130 * mm, 40 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#2b6cb0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#cbd5e0")),
        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#f7fafc")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.6, color=HexColor("#a0aec0"), spaceAfter=3))
    story.append(Paragraph(
        "Generated for Task 6 hand-over • Ezitech Software House • portal.ezitech.org • November 2026",
        styles["Footer"],
    ))

    doc.build(story)
    print(f"Created: {OUTPUT}")

if __name__ == "__main__":
    build()
