import streamlit as st
import requests
import os
import docx
import PyPDF2
import joblib
import json
from dotenv import load_dotenv
from io import BytesIO
from docx import Document

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
JOOBLE_API_KEY = os.getenv('JOOBLE_API_KEY')

# Hugging Face Model URL
HF_MODEL_API = "https://api-inference.huggingface.co/models/jaik256/jobRecommendation"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

# Streamlit setup
st.set_page_config(page_title="AI Career Assistant", layout="wide")
st.title("🚀 AI Career Assistant")

# Helper functions
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

def query_groq(prompt):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
    return response.json()['choices'][0]['message']['content'] if response.ok else f"Error: {response.text}"

def query_hf_model(resume_text):
    payload = {"inputs": resume_text}
    response = requests.post(HF_MODEL_API, headers=HF_HEADERS, json=payload)
    return response.json() if response.ok else []

def query_jooble_api(keywords, location="India"):
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    payload = {"keywords": keywords, "location": location}
    response = requests.post(url, json=payload)
    return response.json().get("jobs", []) if response.ok else []

# Upload resume
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

    if len(resume_content.strip()) > 0:
        st.success("✅ Resume parsed successfully!")
        if len(resume_content) > 4000:
            st.warning("⚠️ Trimming resume to 4000 characters.")
            resume_content = resume_content[:4000]

        # Resume enhancement
        jd_based = st.radio("Want resume tips based on a Job Description?", ('Yes', 'No'))
        if jd_based == 'Yes':
            jd_text = st.text_area("Paste the Job Description here:")
            if jd_text and st.button("Generate JD-based Resume Report"):
                prompt = f"""You are a career expert. Improve this resume based on the JD below:\n\nResume:\n{resume_content}\n\nJD:\n{jd_text}"""
                st.write(query_groq(prompt))
        else:
            role = st.text_input("Enter the job role you're targeting:")
            if role and st.button("Generate General Resume Feedback"):
                prompt = f"""You are a resume consultant. Suggest improvement tips for this resume targeting the role of {role}:\n\n{resume_content}"""
                st.write(query_groq(prompt))

        # Cover Letter
        if st.checkbox("Generate Cover Letter"):
            experience = st.selectbox("Your experience level:", ['Fresher', '1-3 years', '3-5 years', '5+ years'])
            word_limit = st.slider("Cover Letter Length (words):", 100, 500, 300)
            company = st.text_input("Target company:")
            if company and st.button("Generate Cover Letter"):
                prompt = f"""Write a {word_limit}-word cover letter for a {experience} candidate applying to {company}, based on the resume:\n\n{resume_content}"""
                letter = query_groq(prompt)
                st.write(letter)
                buffer = export_docx(letter)
                st.download_button("📄 Download Cover Letter (.docx)", data=buffer, file_name="cover_letter.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # Roadmap
        if st.checkbox("Generate Learning Roadmap"):
            career = st.selectbox("Choose target career:", ['Data Scientist', 'Web Developer', 'ML Engineer', 'Product Manager'])
            if st.button("Generate Roadmap"):
                prompt = f"""Create a complete skill-building roadmap to become a {career}. Include beginner to expert topics and learning resources."""
                st.write(query_groq(prompt))

        # Career Chat
        st.subheader("💬 Ask the AI Career Assistant")
        query = st.text_input("Your career-related question:")
        if query:
            st.write(query_groq(f"You are a career assistant. Help with:\n{query}"))

        # Job Recommendation
        if st.checkbox("🔍 Get Job Recommendations"):
            if st.button("Get Recommended Jobs"):
                with st.spinner("Processing resume and fetching job openings..."):
                    preds = query_hf_model(resume_content)
                    if isinstance(preds, list) and preds:
                        top_keywords = preds[0] if isinstance(preds[0], str) else " ".join(preds[0])
                        jobs = query_jooble_api(top_keywords)
                        if jobs:
                            st.success(f"Top jobs for: **{top_keywords}**")
                            for job in jobs[:5]:
                                st.markdown(f"**🧠 {job['title']}** at *{job['company']}, {job['location']}*")
                                st.markdown(f"- 🔗 [Apply Here]({job['link']})")
                                st.markdown(f"- 📄 Summary: {job['snippet']}")
                                st.markdown("---")
                        else:
                            st.warning("No jobs found. Try adjusting keywords or location.")
                    else:
                        st.error("Model did not return valid output.")
    else:
        st.error("Resume could not be parsed. Please upload a valid file.")
else:
    st.info("☝ Please upload your resume to begin.")
