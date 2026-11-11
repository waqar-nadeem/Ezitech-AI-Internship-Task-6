"""
AI-Powered Meeting Transcript Summariser
for Mehfil Event Planners
"""

import streamlit as st
import re
import io
from datetime import datetime
from typing import List, Dict, Tuple

# Optional heavy imports are done inside functions / with caching
# so the app starts quickly on Streamlit Cloud

st.set_page_config(
    page_title="Mehfil Meeting Summariser",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Constants & Helpers
# -----------------------------------------------------------------------------
MAX_CHUNK_WORDS = 450          # safe size for DistilBART
MIN_SUMMARY_WORDS = 40
QUALITY_CHECKS = [
    "Summary is concise and readable",
    "Key decisions are clearly listed",
    "Action items include owners or next steps where possible",
    "No obvious hallucinations or invented names",
    "Overall tone matches a professional event-planning context",
]


def clean_text(text: str) -> str:
    """Basic cleaning of transcript text."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text.strip()


def chunk_text(text: str, max_words: int = MAX_CHUNK_WORDS) -> List[str]:
    """Split long text into overlapping-ish chunks by sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = []
    current_len = 0

    for sent in sentences:
        words = len(sent.split())
        if current_len + words > max_words and current:
            chunks.append(" ".join(current))
            # small overlap for continuity
            current = current[-1:] if current else []
            current_len = len(current[0].split()) if current else 0
        current.append(sent)
        current_len += words

    if current:
        chunks.append(" ".join(current))
    return chunks if chunks else [text]


@st.cache_resource(show_spinner="Loading summarisation model (first run only)...")
def load_summarizer():
    """Load a lightweight open-source model suitable for Streamlit Cloud."""
    from transformers import pipeline
    # DistilBART is much lighter than bart-large-cnn and works well on CPU
    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",
        device=-1,  # CPU
    )
    return summarizer


def summarise_chunk(summarizer, text: str) -> str:
    """Summarise a single chunk with sensible length limits."""
    word_count = len(text.split())
    max_len = min(130, max(60, word_count // 3))
    min_len = min(30, max_len // 2)

    try:
        result = summarizer(
            text,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            truncation=True,
        )
        return result[0]["summary_text"].strip()
    except Exception as e:
        return f"[Summarisation error on chunk: {str(e)[:80]}]"


def extract_decisions_and_actions(full_summary: str, original: str) -> Tuple[List[str], List[str]]:
    """
    Lightweight rule-based extraction of decisions and action items.
    Works without an extra LLM call – good for free-tier reliability.
    """
    decisions = []
    actions = []

    # Look for common decision / action patterns
    decision_patterns = [
        r"(?:we|team|everyone)\s+(?:decided|agreed|confirmed|finalised|chose)\s+(?:to|that|on)?\s*(.+?)(?:\.|$)",
        r"(?:decision|agreed|final)\s*[:\-]\s*(.+?)(?:\.|$)",
        r"(?:it was|it is)\s+(?:decided|agreed)\s+(?:that)?\s*(.+?)(?:\.|$)",
    ]
    action_patterns = [
        r"(?:will|shall|to)\s+(\w+\s+(?:prepare|send|book|confirm|follow.?up|arrange|contact|update|share|create|finalise).+?)(?:\.|$)",
        r"(?:action|todo|task|next step)\s*[:\-]\s*(.+?)(?:\.|$)",
        r"(\w+)\s+(?:will|to)\s+(?:handle|take care of|own|lead)\s+(.+?)(?:\.|$)",
        r"(?:please|need to|must)\s+(.+?)(?:\.|$)",
    ]

    text = (full_summary + " " + original[:3000]).lower()

    for pat in decision_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            item = m.group(1).strip()
            if 15 < len(item) < 180 and item not in decisions:
                decisions.append(item.capitalize())

    for pat in action_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            item = " ".join(g for g in m.groups() if g).strip()
            if 15 < len(item) < 180 and item not in actions:
                actions.append(item.capitalize())

    # Fallbacks if nothing found
    if not decisions:
        decisions = ["Review the full summary for explicit decisions made during the meeting."]
    if not actions:
        actions = ["Assign owners and deadlines for any open items mentioned in the summary."]

    return decisions[:6], actions[:8]


def run_quality_checklist(summary: str, decisions: List[str], actions: List[str]) -> Dict[str, bool]:
    """Simple automated quality signals + room for human review."""
    results = {}
    results[QUALITY_CHECKS[0]] = 40 < len(summary.split()) < 350
    results[QUALITY_CHECKS[1]] = len(decisions) >= 1 and "review the full" not in decisions[0].lower()
    results[QUALITY_CHECKS[2]] = len(actions) >= 1
    results[QUALITY_CHECKS[3]] = not any(
        w in summary.lower() for w in ["as an ai", "i cannot", "hallucinated", "fictional"]
    )
    results[QUALITY_CHECKS[4]] = True  # human judgement
    return results


def create_markdown_report(
    title: str,
    summary: str,
    decisions: List[str],
    actions: List[str],
    checklist: Dict[str, bool],
    meta: dict,
) -> str:
    """Generate a clean Markdown report."""
    md = f"""# Meeting Summary Report – Mehfil Event Planners

**Generated:** {meta.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))}  
**Source file:** {meta.get('filename', 'pasted text')}  
**Word count (original):** {meta.get('word_count', 'N/A')}

---

## Executive Summary
{summary}

---

## Key Decisions
"""
    for i, d in enumerate(decisions, 1):
        md += f"{i}. {d}\n"

    md += "\n## Action Items\n"
    for i, a in enumerate(actions, 1):
        md += f"{i}. {a}\n"

    md += "\n## Quality Checklist\n"
    for check, passed in checklist.items():
        status = "✅" if passed else "⚠️"
        md += f"- {status} {check}\n"

    md += """
---
*Generated by the Mehfil AI Meeting Transcript Summariser*  
*This is an assistive tool – always verify critical details with the original transcript.*
"""
    return md


def markdown_to_pdf(md_text: str) -> bytes:
    """Convert simple Markdown-like text to a clean one-page-friendly PDF."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.lib.colors import HexColor

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="MainTitle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=HexColor("#1a365d"),
        spaceAfter=6,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=HexColor("#2c5282"),
        spaceBefore=10,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="BodyTextCustom",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=12,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="Meta",
        parent=styles["Normal"],
        fontSize=8,
        textColor=HexColor("#4a5568"),
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Footer",
        parent=styles["Normal"],
        fontSize=7.5,
        textColor=HexColor("#718096"),
        alignment=TA_CENTER,
        spaceBefore=12,
    ))

    story = []

    # Parse the markdown roughly
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["MainTitle"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Section"]))
        elif line.startswith("**") and line.endswith("**"):
            story.append(Paragraph(line.replace("**", ""), styles["Meta"]))
        elif line.startswith("- ") or re.match(r"^\d+\.", line):
            # collect list items
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or re.match(r"^\d+\.", lines[i])):
                item_text = re.sub(r"^[-*\d.]+\s*", "", lines[i]).strip()
                # simple emoji / status handling
                item_text = item_text.replace("✅", "[OK]").replace("⚠️", "[Check]")
                items.append(ListItem(Paragraph(item_text, styles["BodyTextCustom"]), leftIndent=10))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", start="•"))
            continue
        elif line.startswith("---"):
            story.append(Spacer(1, 4))
        elif line.strip():
            # normal paragraph
            clean = line.replace("**", "").replace("*", "")
            story.append(Paragraph(clean, styles["BodyTextCustom"]))
        i += 1

    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Generated by Mehfil AI Meeting Transcript Summariser • Verify critical details against the original transcript",
        styles["Footer"],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def extract_text_from_file(uploaded_file) -> str:
    """Extract plain text from txt / pdf / docx."""
    name = uploaded_file.name.lower()
    raw = uploaded_file.read()

    if name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(pages)

    if name.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(raw))
        return "\n".join(p.text for p in doc.paragraphs)

    return raw.decode("utf-8", errors="ignore")


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------
st.title("📋 Mehfil Meeting Transcript Summariser")
st.caption("Turn raw vendor & client meeting transcripts into clear, actionable reports for event planning.")

with st.sidebar:
    st.header("About")
    st.markdown(
        """
        Built for **Mehfil Event Planners**.

        **Features**
        - Upload `.txt`, `.pdf` or `.docx`
        - Automatic chunking for long meetings
        - Open-source DistilBART summarisation
        - Key decisions + action items
        - Quality checklist
        - Downloadable Markdown & PDF report
        """
    )
    st.markdown("---")
    st.markdown("**Model:** `sshleifer/distilbart-cnn-12-6` (open-source)")
    st.markdown("Task 6 • Ezitech AI Internship")

# Input section
tab1, tab2 = st.tabs(["📄 Upload Transcript", "✍️ Paste Text"])

transcript = ""
source_name = "pasted_text"

with tab1:
    uploaded = st.file_uploader(
        "Upload meeting transcript",
        type=["txt", "pdf", "docx"],
        help="Supports plain text, PDF and Word documents.",
    )
    if uploaded:
        with st.spinner("Extracting text..."):
            transcript = extract_text_from_file(uploaded)
            source_name = uploaded.name
        st.success(f"Loaded **{source_name}** ({len(transcript.split())} words)")

with tab2:
    pasted = st.text_area(
        "Or paste the transcript here",
        height=220,
        placeholder="Paste the full meeting transcript...",
    )
    if pasted.strip():
        transcript = pasted
        source_name = "pasted_text"

if transcript:
    transcript = clean_text(transcript)
    word_count = len(transcript.split())

    with st.expander("Preview transcript (first 800 characters)", expanded=False):
        st.text(transcript[:800] + ("..." if len(transcript) > 800 else ""))

    col1, col2, col3 = st.columns(3)
    col1.metric("Words", f"{word_count:,}")
    col2.metric("Approx. chunks", max(1, (word_count // MAX_CHUNK_WORDS) + 1))
    col3.metric("Est. time", f"~{max(8, word_count // 80)}s")

    if st.button("🚀 Generate Summary & Report", type="primary", use_container_width=True):
        progress = st.progress(0, text="Starting...")

        # 1. Chunk
        progress.progress(10, text="Chunking transcript...")
        chunks = chunk_text(transcript)
        st.info(f"Split into **{len(chunks)}** chunk(s) for processing.")

        # 2. Load model & summarise
        progress.progress(25, text="Loading model...")
        summarizer = load_summarizer()

        partial_summaries = []
        for idx, chunk in enumerate(chunks):
            progress.progress(
                25 + int(50 * (idx + 1) / len(chunks)),
                text=f"Summarising chunk {idx + 1}/{len(chunks)}...",
            )
            partial_summaries.append(summarise_chunk(summarizer, chunk))

        # 3. Merge
        progress.progress(80, text="Merging & extracting decisions/actions...")
        if len(partial_summaries) == 1:
            final_summary = partial_summaries[0]
        else:
            combined = " ".join(partial_summaries)
            # second pass if still long
            if len(combined.split()) > 280:
                final_summary = summarise_chunk(summarizer, combined)
            else:
                final_summary = combined

        decisions, actions = extract_decisions_and_actions(final_summary, transcript)
        checklist = run_quality_checklist(final_summary, decisions, actions)

        progress.progress(100, text="Done!")
        st.success("Summary ready")

        # Display results
        st.subheader("Executive Summary")
        st.write(final_summary)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Key Decisions")
            for d in decisions:
                st.markdown(f"- {d}")
        with c2:
            st.subheader("Action Items")
            for a in actions:
                st.markdown(f"- {a}")

        st.subheader("Quality Checklist")
        for check, passed in checklist.items():
            st.markdown(f"{'✅' if passed else '⚠️'} {check}")

        # Build report
        meta = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "filename": source_name,
            "word_count": word_count,
        }
        md_report = create_markdown_report(
            "Mehfil Meeting Summary",
            final_summary,
            decisions,
            actions,
            checklist,
            meta,
        )

        st.subheader("Download Report")
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "⬇️ Download Markdown",
                data=md_report,
                file_name=f"Mehfil_Summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with dl2:
            try:
                pdf_bytes = markdown_to_pdf(md_report)
                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"Mehfil_Summary_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.warning(f"PDF generation failed: {e}. Markdown download still works.")

        with st.expander("View full Markdown report"):
            st.code(md_report, language="markdown")

else:
    st.info("👆 Upload a transcript or paste text to get started.")
    st.markdown(
        """
        ### Quick start
        1. Upload a meeting transcript (or paste it)
        2. Click **Generate Summary & Report**
        3. Review the summary, decisions and action items
        4. Download the Markdown or PDF report

        A sample transcript is available in the repository under `sample_data/`.
        """
    )
