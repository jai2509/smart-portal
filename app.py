import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')

st.title("AI Career Assistant")

# Resume upload
resume = st.file_uploader("Upload your resume (PDF/DOCX)")
if resume:
    resume_content = resume.read().decode(errors='ignore')
    st.success("Resume uploaded successfully!")

    # Ask for JD-based enhancement
    jd_based = st.radio("Do you want resume enhancement tips based on a job description?", ('Yes', 'No'))
    
    if jd_based == 'Yes':
        jd_text = st.text_area("Paste the job description (JD) here")
        if jd_text and st.button("Generate JD-based Resume Enhancement Report"):
            response = requests.post('https://api.groq.com/generate', headers={'Authorization': f'Bearer {GROQ_API_KEY}'}, json={
                'prompt': f"Give resume enhancement tips for this resume: {resume_content} based on this JD: {jd_text}",
                'max_tokens': 500
            })
            result = response.json().get('text', 'No response')
            st.write(result)
    else:
        position = st.text_input("Enter the position you want to apply for")
        if position and st.button("Generate General Resume Report"):
            response = requests.post('https://api.groq.com/generate', headers={'Authorization': f'Bearer {GROQ_API_KEY}'}, json={
                'prompt': f"Give general resume improvement tips for this resume: {resume_content} targeting the position: {position}",
                'max_tokens': 500
            })
            result = response.json().get('text', 'No response')
            st.write(result)

    # Cover letter generation
    if st.checkbox("Generate a cover letter"):
        experience = st.selectbox("Select your experience level", ['Fresher', '1-3 years', '3-5 years', '5+ years'])
        word_limit = st.slider("Select cover letter word limit", 100, 500, 300)
        company = st.text_input("Enter the target company name")
        if company and st.button("Generate Cover Letter"):
            response = requests.post('https://api.groq.com/generate', headers={'Authorization': f'Bearer {GROQ_API_KEY}'}, json={
                'prompt': f"Write a {word_limit}-word cover letter for a {experience} candidate applying to {company} based on this resume: {resume_content}",
                'max_tokens': 600
            })
            result = response.json().get('text', 'No response')
            st.write(result)

    # Roadmap generator
    if st.checkbox("Generate a learning roadmap"):
        role = st.selectbox("Select role for roadmap", ['Data Scientist', 'Full Stack Developer', 'Product Manager', 'Data Engineer'])
        if st.button("Generate Roadmap"):
            response = requests.post('https://api.groq.com/generate', headers={'Authorization': f'Bearer {GROQ_API_KEY}'}, json={
                'prompt': f"Create a beginner-to-professional roadmap to become a {role} with key skills and milestones.",
                'max_tokens': 700
            })
            result = response.json().get('text', 'No response')
            st.write(result)

    # Chatbot section
    st.subheader("Chat with the AI Assistant")
    user_query = st.text_input("Ask anything")
    if user_query:
        hf_response = requests.post('https://api-inference.huggingface.co/models/google/flan-t5-large',
                                   headers={'Authorization': f'Bearer {HF_TOKEN}'},
                                   json={'inputs': user_query})
        answer = hf_response.json()[0]['generated_text'] if hf_response.ok else 'Error getting response'
        st.write(answer)
