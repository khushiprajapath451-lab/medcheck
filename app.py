# app.py
import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile, datetime
import PyPDF2
api_key = st.secrets["GEMINI_API_KEY"]

# ---------- Page config ----------
st.set_page_config(page_title="MedCheck", page_icon="💉", layout="centered")

# ---------- Styles: light green + white ----------
page_style = """
<style>
/* page background */
[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #f5fff6 0%, #ffffff 45%);
}
/* main container card */
main .block-container {
  background-color: rgba(255,255,255,0.95);
  padding: 2rem 2rem 2.5rem 2rem;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.05);
}

/* headers */
h1, h2, h3 {
  color: #0f5132;
}

/* button style */
.stButton>button {
  background: linear-gradient(90deg,#a7e3b8,#7fd19a);
  color: #034a20;
  border-radius: 8px;
  padding: 0.5rem 1rem;
}

/* small text */
.small-muted {
  color: #436a53;
  font-size: 0.9rem;
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# ---------- Title ----------
st.title("MedCheck — AI for Patient Safety")
st.markdown("<div class='small-muted'>Understand a diagnosis, check how urgent surgery is, and save a shareable report.</div>", unsafe_allow_html=True)
st.write("---")

# ---------- Configure Gemini from secrets ----------
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API key missing. Add GEMINI_API_KEY in Streamlit secrets before running.")
else:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-pro")

# ---------- Form for patient data and input method ----------
with st.form("patient_form"):
    st.subheader("Patient details")
    patient_name = st.text_input("Full name")
    patient_age = st.number_input("Age", min_value=0, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Select", "Female", "Male", "Other"])

    st.write("### Provide the doctor's advice or upload a report")
    input_mode = st.radio("Input method", ["Type diagnosis", "Upload report"])

    typed_text = ""
    uploaded_text = ""

    if input_mode == "Type diagnosis":
        typed_text = st.text_area("Type the symptoms or doctor's advice here")
    else:
        uploaded_file = st.file_uploader("Upload PDF or TXT report", type=["pdf", "txt"])
        if uploaded_file:
            # Read PDF or plain text
            if uploaded_file.type == "application/pdf":
                try:
                    reader = PyPDF2.PdfReader(uploaded_file)
                    pages = []
                    for p in reader.pages:
                        text = p.extract_text() or ""
                        pages.append(text)
                    uploaded_text = "\n".join(pages)
                except Exception as e:
                    st.error(f"Could not read PDF: {e}")
            else:
                uploaded_text = uploaded_file.read().decode("utf-8")

    analyze_clicked = st.form_submit_button("Analyze my condition")

# ---------- Analysis & results ----------
if analyze_clicked:
    if gender == "Select" or not patient_name.strip():
        st.warning("Please fill name and gender to proceed.")
    else:
        diagnosis_text = typed_text if input_mode == "Type diagnosis" else uploaded_text
        if not diagnosis_text.strip():
            st.warning("Please type or upload the doctor's advice or report.")
        else:
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("GEMINI_API_KEY missing in secrets — analysis cannot run.")
            else:
                with st.spinner("Analyzing..."):
                    prompt = f"""
Patient: {patient_name}, Age: {patient_age}, Gender: {gender}

Doctor's advice / report:
{diagnosis_text}

You are an ethical medical AI assistant. In plain language:
1) Explain what this likely means.
2) Assess surgery urgency using: 🟢 Low, 🟡 Medium, 🔴 High.
3) Give 2 reasons for the assessment.
4) Suggest safe next steps and questions to ask a doctor.
Keep tone calm and factual.
"""
                    try:
                        response = model.generate_content(prompt)
                        ai_text = response.text
                    except Exception as e:
                        st.error(f"AI request failed: {e}")
                        ai_text = ""

                if ai_text:
                    st.success("Analysis complete")
                    st.markdown(ai_text)

                    # highlight urgency
                    if "🔴" in ai_text:
                        st.markdown("### 🔴 Surgery Likelihood: High")
                    elif "🟡" in ai_text:
                        st.markdown("### 🟡 Surgery Likelihood: Medium")
                    elif "🟢" in ai_text:
                        st.markdown("### 🟢 Surgery Likelihood: Low")
                    else:
                        st.markdown("### ⚪ Surgery Likelihood: Not determined")

                    # ---------- PDF download ----------
                    if st.button("Download AI report (PDF)"):
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            c = canvas.Canvas(tmp.name, pagesize=letter)
                            w, h = letter
                            c.setFont("Helvetica-Bold", 16)
                            c.drawString(50, h - 50, "MedCheck — AI Report")
                            c.setFont("Helvetica", 10)
                            c.drawString(50, h - 70, f"Date: {datetime.date.today()}")
                            c.drawString(50, h - 95, f"Name: {patient_name}   Age: {patient_age}   Gender: {gender}")

                            c.setFont("Helvetica-Bold", 12)
                            c.drawString(50, h - 125, "Diagnosis / Report:")
                            text = c.beginText(50, h - 140)
                            for line in diagnosis_text.splitlines():
                                text.textLine(line[:120])
                            c.drawText(text)

                            c.setFont("Helvetica-Bold", 12)
                            c.drawString(50, h - 300, "AI Analysis:")
                            text = c.beginText(50, h - 315)
                            for line in ai_text.splitlines():
                                text.textLine(line[:120])
                            c.drawText(text)

                            c.showPage()
                            c.save()

                            with open(tmp.name, "rb") as fp:
                                st.download_button(
                                    label="⬇ Download PDF",
                                    data=fp,
                                    file_name=f"MedCheck_Report_{patient_name.replace(' ','_')}.pdf",
                                    mime="application/pdf"
                                )
