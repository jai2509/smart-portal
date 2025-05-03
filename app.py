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
st.title("🚀 AI Career Assistant")

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

def get_job_recommendations(resume, experience_years, stream, expected_salary):
    API_URL = "https://api-inference.huggingface.co/models/jaik256/jobRecommendation"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": {
            "resume_text": resume,
            "experience_level": experience_years,
            "graduation_year": graduation_year,
            "stream": stream,
            "expected_salary": expected_salary
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_jooble_jobs(keywords, experience_years):
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    payload = {
        'keywords': keywords,
        'experience': experience_years
    }
    response = requests.post(url, json=payload)
    if response.ok:
        jobs = response.json().get('jobs', [])
        return [f"{job['title']} at {job['company']} ({job['location']})" for job in jobs]
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
        
        experience_input = st.selectbox("Select your experience level:", ["Fresher", "1-3 years", "3-5 years", "5+ years"])
        graduation_year = st.text_input("Graduation year (e.g., 2023)")
        stream = st.text_input("Graduation stream (e.g., Computer Science)")
        expected_salary = st.text_input("Expected salary (in USD or your currency)")

        # Calculate experience from graduation year
        current_year = datetime.now().year
        try:
            grad_year_int = int(graduation_year)
            auto_experience = max(1, current_year - grad_year_int)
        except:
            auto_experience = 1

        st.subheader("🔍 Suggested Jobs")
        if st.button("Get Recommended Jobs"):
            with st.spinner("Fetching recommendations..."):
                jobs = get_job_recommendations(resume_content, auto_experience, stream, expected_salary)
                if jobs:
                    for idx, job in enumerate(jobs, 1):
                        st.markdown(f"**{idx}.** {job}")
                else:
                    jooble_jobs = get_jooble_jobs(stream, auto_experience)
                    if jooble_jobs:
                        for idx, job in enumerate(jooble_jobs, 1):
                            st.markdown(f"**{idx}.** {job}")
                    else:
                        st.info("No suitable jobs found at this time.")
    else:
        st.error("Could not extract text from the uploaded resume.")
else:
    st.info("☝ Please upload your resume to get started.")
