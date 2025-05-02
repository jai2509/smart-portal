import streamlit as st
import requests
import os
import docx
import PyPDF2
from io import BytesIO
from docx import Document
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')

st.set_page_config(page_title="AI Career Assistant", layout="wide")
st.title("🚀 AI Career Assistant")

# Text extraction helpers
def extract_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    except Exception:
        return ""

def extract_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() or "" for page in reader.pages])
    except Exception:
        return ""

# Groq API
def query_groq(prompt):
    if len(prompt) > 5000:
        prompt = prompt[:5000]
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
    if response.ok:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.text}"

# Hugging Face (Career-Focused Model)
def query_huggingface(input_text):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": input_text}
    url = "https://api-inference.huggingface.co/models/MBZUAI/LaMini-Flan-T5-783M"
    response = requests.post(url, headers=headers, json=payload)
    if response.ok:
        return response.json()[0]['generated_text']
    else:
        return f"Error: {response.text}"

# DOCX Export Helper
def export_docx(text, filename="cover_letter.docx"):
    doc = Document()
    for line in text.strip().split('\n'):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Resume Upload
resume = st.file_uploader("Upload your resume (PDF, DOCX, or TXT)")
resume_content = ""

if resume:
    ext = resume.name.split('.')[-1].lower()
    if ext == 'pdf':
        resume_content = extract_pdf(resume)
    elif ext == 'docx':
        resume_content = extract_docx(resume)
    elif ext == 'txt':
        resume_content = resume.read().decode(errors='ignore')
    else:
        st.error("Unsupported file format. Please upload PDF, DOCX, or TXT.")

    if resume_content.strip():
        if len(resume_content) > 4000:
            st.warning("⚠️ Resume is large; trimming to 4000 characters.")
            resume_content = resume_content[:4000]

        st.success("✅ Resume parsed successfully!")
        jd_based = st.radio("Do you want resume enhancement tips based on a Job Description (JD)?", ('Yes', 'No'))

        if jd_based == 'Yes':
            jd_text = st.text_area("Paste the Job Description here:")
            if jd_text and st.button("Generate JD-based Resume Enhancement Report"):
                if len(jd_text) > 2000:
                    st.warning("⚠️ JD text too long; trimming.")
                    jd_text = jd_text[:2000]
                with st.spinner("Generating..."):
                    prompt = f"Provide resume enhancement tips for this resume:\n{resume_content}\nBased on this JD:\n{jd_text}"
                    st.write(query_groq(prompt))
        else:
            position = st.text_input("Enter the position you want to apply for:")
            if position and st.button("Generate General Resume Report"):
                with st.spinner("Generating..."):
                    prompt = f"Give general resume improvement tips for this resume:\n{resume_content}\nTargeting the position: {position}"
                    st.write(query_groq(prompt))

        # Cover Letter
        if st.checkbox("Generate a cover letter"):
            experience = st.selectbox("Select your experience level:", ['Fresher', '1-3 years', '3-5 years', '5+ years'])
            word_limit = st.slider("Select cover letter word limit:", 100, 500, 300)
            company = st.text_input("Enter the target company name:")
            if company and st.button("Generate Cover Letter"):
                with st.spinner("Generating cover letter..."):
                    prompt = f"Write a {word_limit}-word cover letter for a {experience} candidate applying to {company} based on this resume:\n{resume_content}"
                    cover_text = query_groq(prompt)
                    st.write(cover_text)

                    # Export option
                    buffer = export_docx(cover_text)
                    st.download_button(
                        label="📄 Download Cover Letter (.docx)",
                        data=buffer,
                        file_name="cover_letter.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

        # Roadmap Generator
        if st.checkbox("Generate a learning roadmap"):
            role = st.selectbox("Select role for roadmap:", ['Data Scientist', 'Full Stack Developer', 'Product Manager', 'Data Engineer'])
            if st.button("Generate Roadmap"):
                with st.spinner("Generating roadmap..."):
                    prompt = f"Create a roadmap to become a {role}, starting from basics to advanced with skills and milestones."
                    st.write(query_groq(prompt))

        # Chatbot
        st.subheader("💬 Chat with the AI Career Assistant")
        user_query = st.text_input("Ask your career-related question:")
        if user_query:
            with st.spinner("Thinking..."):
                result = query_huggingface(user_query)
                st.write(result)
    else:
        st.error("Could not extract text from the uploaded resume.")
else:
    st.info("☝ Please upload your resume to get started.")
