import streamlit as st
import requests
import os
import docx
import PyPDF2
from io import BytesIO
from docx import Document
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')
JOOBLE_API_KEY = os.getenv('JOOBLE_API_KEY')

st.set_page_config(page_title="AI Career Assistant", layout="wide")
st.title("🚀 SmartHire :AI JOB PORTAL ")

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
        return None

def get_jooble_jobs(keywords, experience_years, location):
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    payload = {
        'keywords': keywords,
        'experience': experience_years,
        'location': location
    }
    response = requests.post(url, json=payload)
    if response.ok:
        jobs = response.json().get('jobs', [])
        return [{
            'title': job['title'],
            'company': job['company'],
            'location': job['location'],
            'link': job.get('link', '')
        } for job in jobs]
    else:
        return []

def export_docx(text, filename="cover_letter.docx"):
    doc = Document()
    for line in text.strip().split('\n'):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

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

        graduation_year = st.text_input("Graduation year (e.g., 2023)")
        stream = st.text_input("Graduation stream (e.g., Computer Science)")
        expected_salary = st.text_input("Expected salary (in USD or your currency)")
        location = st.text_input("Preferred job location (e.g., New York, Remote)")

        current_year = datetime.now().year
        try:
            grad_year_int = int(graduation_year)
            auto_experience = max(1, current_year - grad_year_int)
        except:
            auto_experience = 1

        st.subheader("🔍 Suggested Jobs")
        if st.button("Get Recommended Jobs"):
            with st.spinner("Fetching recommendations..."):
                jooble_jobs = get_jooble_jobs(stream, auto_experience, location)
                if jooble_jobs:
                    for idx, job in enumerate(jooble_jobs, 1):
                        st.markdown(f"**{idx}.** [{job['title']} at {job['company']} ({job['location']})]({job['link']})")
                else:
                    st.info("No suitable jobs found at this time.")

        st.subheader("✍️ Resume Improvement Tips")
        if st.button("Get Resume Tips"):
            tips = query_groq(f"Please provide resume improvement tips for the following text:\n{resume_content}")
            if tips:
                st.write(tips)

        st.subheader("📝 Generate Cover Letter")
        if st.button("Generate Cover Letter"):
            cover_letter = query_groq(f"Generate a professional cover letter for this resume:\n{resume_content}")
            if cover_letter:
                st.download_button("Download Cover Letter", export_docx(cover_letter), file_name="cover_letter.docx")

        st.subheader("🗺️ Career Roadmap")
        if st.button("Get Career Roadmap"):
            roadmap = query_groq(f"Generate a career roadmap for someone with this background:\n{resume_content}")
            if roadmap:
                st.write(roadmap)

        st.subheader("💬 Career Chatbot")
        user_question = st.text_input("Ask the AI Career Assistant a question:")
        if user_question:
            answer = query_groq(f"Question: {user_question}\nBased on this resume:\n{resume_content}")
            if answer:
                st.write(answer)
    else:
        st.error("Could not extract text from the uploaded resume.")
else:
    st.info("☝ Please upload your resume to get started.")
