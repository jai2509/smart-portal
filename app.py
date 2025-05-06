import streamlit as st
import requests
import os
import docx
import PyPDF2
import re
import logging
from io import BytesIO
from docx import Document
from datetime import datetime
from dotenv import load_dotenv
from collections import Counter
from functools import lru_cache
from fuzzywuzzy import fuzz

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')
JOOBLE_API_KEY = os.getenv('JOOBLE_API_KEY')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

st.set_page_config(page_title="AI Career Assistant", layout="wide")
st.title("🚀 SmartHire: AI JOB PORTAL")

logging.basicConfig(level=logging.INFO)

# --- Resume Extraction ---
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

def export_docx(text, filename="cover_letter.docx"):
    doc = Document()
    for line in text.strip().split('\n'):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- GROQ Query ---
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

# --- Skill Synonym Expansion ---
SKILL_SYNONYMS = {
    "python": ["py"],
    "java": ["java programming"],
    "sql": ["database"],
    "javascript": ["js"],
    "machine learning": ["ml"],
    "data analysis": ["analytics"]
}

def expand_skills(skills):
    expanded = set(skills)
    for skill in skills:
        synonyms = SKILL_SYNONYMS.get(skill.lower(), [])
        expanded.update(synonyms)
    return list(expanded)

# --- Job Fetching ---
@lru_cache(maxsize=10)
def fetch_jobs():
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {"query": "software developer", "num_pages": 1}
    response = requests.get(url, headers=headers, params=params)
    if response.ok:
        return response.json().get("data", [])
    else:
        logging.error(f"API error: {response.status_code}")
        return []

def fuzzy_match(skill, text, threshold=85):
    return fuzz.partial_ratio(skill.lower(), text.lower()) >= threshold

def match_jobs(user_skills):
    jobs = fetch_jobs()
    expanded_skills = expand_skills(user_skills)
    matched_jobs = []
    missing_skills_per_job = {}
    all_missing_skills = []

    for job in jobs:
        job_text = f"{job['job_title']} {job['job_description']}"
        matched = any(fuzzy_match(skill, job_text) for skill in expanded_skills)
        if matched:
            matched_jobs.append(job)
            missing_skills = [skill for skill in expanded_skills if not fuzzy_match(skill, job_text)]
            missing_skills_per_job[job['job_id']] = missing_skills
            all_missing_skills.extend(missing_skills)

    prioritized_missing_skills = Counter(all_missing_skills).most_common()
    return matched_jobs, missing_skills_per_job, prioritized_missing_skills

def generate_skill_gap_report(matched_jobs, missing_skills_per_job, prioritized_missing_skills):
    report = "## Skill Gap Report\n\n"
    report += "### Prioritized Missing Skills:\n"
    for skill, count in prioritized_missing_skills:
        report += f"- {skill} (missing in {count} jobs)\n"
    report += "\n### Matched Jobs and Missing Skills:\n"
    for job in matched_jobs:
        job_id = job['job_id']
        report += f"- {job['job_title']} at {job['employer_name']} ({job['job_city']})\n"
        report += f"  Missing skills: {', '.join(missing_skills_per_job.get(job_id, [])) or 'None'}\n"
    return report

# --- Streamlit App ---
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

        st.subheader("🔍 Suggested Jobs (Jooble)")
        if st.button("Get Recommended Jobs"):
            st.info("This section currently uses Jooble API.")

        st.subheader("✍️ Resume Improvement Tips")
        job_position = st.text_input("Which position are you applying for?")
        if st.button("Get Resume Tips"):
            if job_position:
                tips_prompt = f"Give resume improvement suggestions for someone applying to a {job_position} position. Here's the resume:\n{resume_content}"
                tips = query_groq(tips_prompt)
                if tips:
                    st.write(tips)
            else:
                st.warning("Please specify the job position you're applying for.")

        st.subheader("📝 Generate Cover Letter")
        company_name = st.text_input("What company are you applying to?")
        word_limit = st.slider("Desired word count for the cover letter", min_value=300, max_value=500, value=350, step=10)
        if st.button("Generate Cover Letter"):
            if company_name:
                cover_prompt = (
                    f"Generate a professional and tailored cover letter around {word_limit} words "
                    f"for the following resume. The user is applying to {company_name}:\n{resume_content}"
                )
                cover_letter = query_groq(cover_prompt)
                if cover_letter:
                    st.download_button("Download Cover Letter", export_docx(cover_letter), file_name="cover_letter.docx")
            else:
                st.warning("Please enter the company name you're applying to.")

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

        st.subheader("🚀 Advanced Job Match & Skill Gap Analysis")
        user_skills_input = st.text_input("Enter your current skills (comma-separated)")
        if st.button("Analyze Jobs and Gaps"):
            if user_skills_input:
                user_skills = [skill.strip() for skill in user_skills_input.split(",")]
                matched_jobs, missing_skills_per_job, prioritized_missing_skills = match_jobs(user_skills)
                report = generate_skill_gap_report(matched_jobs, missing_skills_per_job, prioritized_missing_skills)
                st.markdown(report)
            else:
                st.warning("Please enter at least one skill to analyze.")
    else:
        st.error("Could not extract text from the uploaded resume.")
else:
    st.info("☝ Please upload your resume to get started.")
