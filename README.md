# 📋 Mehfil Meeting Transcript Summariser

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mehfil-summariser.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> AI-powered tool that turns raw meeting transcripts into concise, actionable reports for **Mehfil Event Planners**.

---

## ✨ Features

- **Upload** `.txt`, `.pdf` or `.docx` transcripts (or paste text)
- **Automatic chunking** for long meetings so the model stays within limits
- **Open-source summarisation** using DistilBART (`sshleifer/distilbart-cnn-12-6`)
- Extracts **key decisions** and **action items**
- Simple **quality checklist** for the generated summary
- Downloadable **Markdown** and **PDF** reports
- Clean, professional Streamlit interface ready for non-technical users

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/mehfil-summariser.git
cd mehfil-summariser

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Open the URL shown in the terminal (usually http://localhost:8501).

---

## ☁️ Deploy to Streamlit Community Cloud

1. Push this repository to GitHub (public repo recommended).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo → branch `main` → main file path `app.py`.
4. Click **Deploy**.
5. After the app is live, copy the public URL and update the badge + link at the top of this README.

**Notes for first deployment**
- The model downloads on the first run (can take 1–2 minutes). Subsequent runs are faster because of Streamlit’s resource cache.
- Free tier is CPU-only; DistilBART is intentionally chosen because it runs reliably without a GPU.

---

## 📂 Project Structure

```
mehfil-summariser/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── HandOver_Mehfil.pdf    # One-page hand-over document
├── sample_data/
│   └── sample_transcript.txt
└── assets/                # Optional images / logos
```

---

## 🧪 Sample Usage

1. Open the app.
2. Go to the **Upload Transcript** tab and select `sample_data/sample_transcript.txt`,  
   **or** paste the content into the **Paste Text** tab.
3. Click **Generate Summary & Report**.
4. Review the executive summary, key decisions, action items and quality checklist.
5. Download the Markdown or PDF report.

---

## 🛠️ Tech Stack

| Component              | Choice                                      |
|------------------------|---------------------------------------------|
| UI                     | Streamlit                                   |
| Summarisation model    | DistilBART (sshleifer/distilbart-cnn-12-6)  |
| PDF generation         | ReportLab                                   |
| Document parsing       | pypdf + python-docx                         |
| Deployment             | Streamlit Community Cloud                   |

---

## ⚠️ Limitations

- The model is extractive/abstractive hybrid and can occasionally miss nuanced decisions; always cross-check critical items against the original transcript.
- Very long transcripts (> ~8 000 words) are processed in multiple chunks; a final merge pass is applied but may still lose some fine detail.
- Action-item extraction is rule-based (no second LLM call) to keep the free-tier deployment fast and reliable.
- First load on Streamlit Cloud downloads the model weights (~300 MB); subsequent sessions use the cache.

---

## 📄 Hand-over Document

See **[HandOver_Mehfil.pdf](HandOver_Mehfil.pdf)** for a one-page summary of architecture, usage and limitations (required for Task 6).

---

## 👤 Author

**Waqar Nadeem**  
Ezitech AI Internship – Intermediate Level  
Client: Mehfil Event Planners  
Tasks 1–6 completed (27 Oct – 11 Nov 2026)

---

## License

MIT
