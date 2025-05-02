import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')

st.set_page_config(page_title="AI Career Assistant", layout="wide")
st.title("🚀 AI Career Assistant")

# Helper function for Groq API (chat)
def query_groq(prompt):
    MAX_CHARS = 5500  # Stay well under token limits
    if len(prompt) > MAX_CHARS:
        prompt = prompt[:MAX_CHARS]
    
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

# Helper function for Hugging Face API (chatbot)
def query_huggingface(input_text):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": input_text}
    response = requests.post("https://api-inference.huggingface.co/models/google/flan-t5-large", headers=headers, json=payload)
    if response.ok:
        return response.json()[0]['generated_text']
    else:
        return f"Error: {response.text}"

# Upload resume
resume = st.file_uploader("Upload your resume (PDF/DOCX/TXT)")
if resume:
    resume_content = resume.read().decode(errors='ignore')
    if len(resume_content) > 4000:
        st.warning("⚠️ Your resume is too large; trimming to first 4000 characters to fit API limits.")
        resume_content = resume_content[:4000]
    
    st.success("✅ Resume uploaded successfully!")

    # Resume enhancement
    jd_based = st.radio("Do you want resume enhancement tips based on a Job Description (JD)?", ('Yes', 'No'))

    if jd_based == 'Yes':
        jd_text = st.text_area("Paste the Job Description here:")
        if jd_text and st.button("Generate JD-based Resume Enhancement Report"):
            if len(jd_text) > 2000:
                st.warning("⚠️ JD text too long; trimming to first 2000 characters.")
                jd_text = jd_text[:2000]
            with st.spinner("Generating report..."):
                prompt = f"Provide resume enhancement tips for this resume (resume is trimmed):\n{resume_content}\nBased on this JD:\n{jd_text}"
                result = query_groq(prompt)
                st.write(result)
    else:
        position = st.text_input("Enter the position you want to apply for:")
        if position and st.button("Generate General Resume Report"):
            with st.spinner("Generating report..."):
                prompt = f"Provide general resume improvement tips for this resume (resume is trimmed):\n{resume_content}\nTargeting the position:\n{position}"
                result = query_groq(prompt)
                st.write(result)

    # Cover letter generation
    if st.checkbox("Generate a cover letter"):
        experience = st.selectbox("Select your experience level:", ['Fresher', '1-3 years', '3-5 years', '5+ years'])
        word_limit = st.slider("Select cover letter word limit:", 100, 500, 300)
        company = st.text_input("Enter the target company name:")
        if company and st.button("Generate Cover Letter"):
            with st.spinner("Generating cover letter..."):
                prompt = f"Write a {word_limit}-word cover letter for a {experience} candidate applying to {company} based on this resume (resume is trimmed):\n{resume_content}"
                result = query_groq(prompt)
                st.write(result)

    # Roadmap generator
    if st.checkbox("Generate a learning roadmap"):
        role = st.selectbox("Select role for roadmap:", ['Data Scientist', 'Full Stack Developer', 'Product Manager', 'Data Engineer'])
        if st.button("Generate Roadmap"):
            with st.spinner("Generating roadmap..."):
                prompt = f"Create a beginner-to-professional roadmap to become a {role} with key skills, learning steps, and milestones."
                result = query_groq(prompt)
                st.write(result)

    # Chatbot section
    st.subheader("💬 Chat with the AI Assistant")
    user_query = st.text_input("Ask anything:")
    if user_query:
        with st.spinner("Thinking..."):
            result = query_huggingface(user_query)
            st.write(result)
else:
    st.info("☝ Please upload your resume to start.")
