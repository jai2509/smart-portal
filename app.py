import streamlit as st
import requests
import os
import docx
import PyPDF2
import joblib
from io import BytesIO
from docx import Document
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download

load_dotenv()

# Load Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")

# Load job recommendation model from Hugging Face (downloaded locally)
MODEL_REPO = "jaik256/jobRecommendation"
MODEL_FILENAME = "my_model.joblib"
model_path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILENAME)
model = joblib.load(model_path)

st.set_page_config(page_title="AI Career Assistant", layout="wide")
st.title("🚀 AI Career Assistant")

# Resume extract helpers
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

# Groq API chat
def query_groq(prompt):
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

# Export cover letter

def export_docx(text, filename="cover_letter.docx"):
    doc = Document()
    for line in text.strip().split('\n'):
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Job search using Jooble
def search_jobs(keyword, location="India"):
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    payload = {
        "keywords": keyword,
        "location": location,
        "page": 1,
        "searchMode": "1"
    }
    response = requests.post(url, json=payload)
    if response.ok:
        return response.json().get("jobs", [])
    else:
        return []

# Upload Resume
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
        st.error("Unsupported file format.")

    if resume_content.strip():
        st.success("✅ Resume parsed successfully!")

        # Predict job role
        st.subheader("🔍 Job Role Prediction and Recommendations")
        features = st.text_area("Paste extracted or summarized features from your resume:", resume_content[:500])
        if st.button("Get Job Role & Job Recommendations"):
            with st.spinner("Predicting and searching jobs..."):
                try:
                    predicted_role = model.predict([features])[0]
                    st.success(f"🎯 Predicted Job Role: {predicted_role}")
                    jobs = search_jobs(predicted_role)
                    if jobs:
                        for job in jobs[:5]:
                            st.markdown(f"**{job['title']}** at {job['company']} in {job['location']}")
                            st.markdown(f"[Apply Here]({job['link']})")
                            st.write(job.get('snippet', ''))
                    else:
                        st.warning("No jobs found.")
                except Exception as e:
                    st.error(f"❌ Prediction/Search failed: {e}")

        # Cover Letter
        if st.checkbox("Generate a cover letter"):
            experience = st.selectbox("Select your experience level:", ['Fresher', '1-3 years', '3-5 years', '5+ years'])
            word_limit = st.slider("Select cover letter word limit:", 100, 500, 300)
            company = st.text_input("Enter the target company name:")
            if company and st.button("Generate Cover Letter"):
                prompt = f"""Write a {word_limit}-word professional cover letter for a {experience} candidate applying to {company}, using the following resume:

{resume_content[:1000]}

Maintain a formal tone."""
                cover_text = query_groq(prompt)
                st.write(cover_text)
                buffer = export_docx(cover_text)
                st.download_button("📄 Download Cover Letter", data=buffer, file_name="cover_letter.docx")

        # Roadmap
        if st.checkbox("Generate a learning roadmap"):
            role = st.selectbox("Select role for roadmap:", ['Data Scientist', 'Full Stack Developer', 'Product Manager', 'Data Engineer'])
            if st.button("Generate Roadmap"):
                prompt = f"""Create a roadmap to become a {role}. Include beginner, intermediate, and advanced skills with tools and resources."""
                st.write(query_groq(prompt))

        # Chat
        st.subheader("💬 Ask the AI Career Assistant")
        question = st.text_input("Ask your career-related question:")
        if question:
            response = query_groq(f"Answer the following career query in bullet points: {question}")
            st.write(response)
    else:
        st.error("Could not extract text from the resume.")
else:
    st.info("☝ Upload a resume to get started.")
