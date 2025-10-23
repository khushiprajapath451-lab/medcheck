# app.py
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile, datetime
import PyPDF2

# ---------- Page config ----------
st.set_page_config(page_title="MedCheck", page_icon="💉", layout="centered")

# ---------- Title ----------
st.title("MedCheck — AI for Patient Safety")
st.write("Understand a diagnosis, check how urgent surgery is, and save a shareable report.")
st.write("---")

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
            # ----- Placeholder AI Analysis -----
            ai_text = "AI analysis disabled — using placeholder text.\nYou can later integrate Gemini AI here."
            st.success("Analysis complete")
            st.markdown(ai_text)
            st.markdown("### ⚪ Surgery Likelihood: Not determined")

            # ---------- PDF download ----------
            if st.button("Download Report (PDF)"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    c = canvas.Canvas(tmp.name, pagesize=letter)
                    w, h = letter
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(50, h - 50, "MedCheck — Patient Report")
                    c.setFont("Helvetica", 10)
                    c.drawString(50, h - 70, f"Date: {datetime.date.today()}")
                    c.drawString(50, h - 95, f"Name: {patient_name}   Age: {patient_age}   Gender: {gender}")

                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(50, h - 125, "Diagnosis / Report:")
                    text_obj = c.beginText(50, h - 140)
                    for line in diagnosis_text.splitlines():
                        text_obj.textLine(line[:120])
                    c.drawText(text_obj)

                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(50, h - 300, "AI Analysis:")
                    text_obj = c.beginText(50, h - 315)
                    for line in ai_text.splitlines():
                        text_obj.textLine(line[:120])
                    c.drawText(text_obj)

                    c.showPage()
                    c.save()

                    with open(tmp.name, "rb") as fp:
                        st.download_button(
                            label="⬇ Download PDF",
                            data=fp,
                            file_name=f"MedCheck_Report_{patient_name.replace(' ','_')}.pdf",
                            mime="application/pdf"
                        )

