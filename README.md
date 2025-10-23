# 💉 MedCheck – AI for Patient Safety

MedCheck is an interactive AI-powered app that helps patients understand their medical diagnosis, assess the urgency of surgery, and generate a personalized, downloadable report.  
It supports both typed diagnosis input and uploading medical reports (PDF/TXT). The AI provides educational guidance, not medical advice.

---

## 🌟 Features

- User-friendly **patient information form** (Name, Age, Gender)
- Input options:
  - Type diagnosis or symptoms
  - Upload a medical report (PDF or TXT)
- **AI analysis** using Google Gemini API:
  - Explains the condition in simple language
  - Rates surgery urgency: 🟢 Low | 🟡 Medium | 🔴 High
  - Provides reasoning and safe next steps
- **Downloadable PDF report** summarizing patient info, diagnosis, and AI guidance
- Light-green + white background for clean, professional design
- Ethical AI design: calm, factual, and educational tone

---

## ⚙️ Tech Stack

- **Frontend**: Streamlit
- **AI**: Google Gemini API (Generative AI)
- **PDF generation**: ReportLab
- **PDF/Text parsing**: PyPDF2
- **Hosting**: Streamlit Community Cloud or Google Cloud Run
- **Python version**: 3.10+ recommended

---

## 🧰 Installation & Local Setup

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/medcheck.git
cd medcheck
