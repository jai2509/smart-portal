import streamlit as st
import base64
import os
import fitz  # PyMuPDF
import docx2txt
import requests
from streamlit_lottie import st_lottie

# ================================
# THEME SETUP
# ================================
theme = st.sidebar.selectbox("Choose Theme", ["Light", "Dark", "Vibrant"])

if theme == "Light":
    primaryColor = "#4CAF50"
    backgroundColor = "#FFFFFF"
    secondaryBackgroundColor = "#F0F2F6"
    textColor = "#000000"
elif theme == "Dark":
    primaryColor = "#BB86FC"
    backgroundColor = "#121212"
    secondaryBackgroundColor = "#1F1F1F"
    textColor = "#FFFFFF"
else:  # Vibrant
    primaryColor = "#FF5722"
    backgroundColor = "#FFF3E0"
    secondaryBackgroundColor = "#FFE0B2"
    textColor = "#000000"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {backgroundColor};
        color: {textColor};
    }}
    .stButton>button {{
        background-color: {primaryColor};
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ================================
# HELPER FUNCTION FOR LOTTIE
# ================================
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_ai = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")

# ================================
# SIDEBAR NAVIGATION
# ================================
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", [
    "🏠 Home", "📤 Upload Resume", "💼 Job Recommendations", 
    "📌 Resume Tips", "✍️ Cover Letter Generator", 
    "🗺️ Career Roadmap", "💬 Career Chatbot"])

# ================================
# PAGE CONTENT
# ================================
if selection == "🏠 Home":
    st.title("Welcome to SmartHire: AI Job Portal")
    st_lottie(lottie_ai, height=250)
    st.markdown("""
    ### 🚀 What You Can Do Here:
    - Upload and analyze your resume
    - Get AI-powered job recommendations
    - Receive personalized resume tips
    - Generate professional cover letters
    - Plan your career roadmap
    - Interact with an AI career advisor
    """)

elif selection == "📤 Upload Resume":
    st.header("📤 Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a resume file (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], help="Upload your resume to receive personalized job insights.")

    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1]

        if file_type == 'pdf':
            text = ""
            pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in pdf:
                text += page.get_text()

        elif file_type == 'docx':
            text = docx2txt.process(uploaded_file)

        else:  # txt
            text = uploaded_file.read().decode("utf-8")

        st.success("Resume successfully processed!")
        st.text_area("Parsed Resume Text", text, height=300)

elif selection == "💼 Job Recommendations":
    st.header("💼 Job Recommendations")
    st.markdown("""Provide your details to get job suggestions using AI.
    """)
    experience = st.slider("Years of Experience", 0, 30, 2)
    expected_salary = st.number_input("Expected Salary ($)", min_value=0)
    graduation_year = st.text_input("Graduation Year", help="e.g., 2023")
    stream = st.text_input("Field of Study", help="e.g., Computer Science")

    if st.button("Get Recommendations"):
        st.info("🔍 Fetching job recommendations using your details and resume...")
        # Placeholder logic
        st.success("Here are your top job matches:")
        st.write("1. Software Engineer at ABC Corp")
        st.write("2. Data Analyst at XYZ Ltd")

elif selection == "📌 Resume Tips":
    st.header("📌 Personalized Resume Tips")
    st.markdown("AI-generated suggestions will appear here based on your uploaded resume.")
    st.write("- Add measurable results to your achievements.")
    st.write("- Highlight your latest project experiences.")

elif selection == "✍️ Cover Letter Generator":
    st.header("✍️ Cover Letter Generator")
    word_count = st.slider("Word Limit", 50, 500, 150)
    job_title = st.text_input("Target Job Title", help="e.g., Data Scientist")

    if st.button("Generate Cover Letter"):
        st.info("Creating your cover letter...")
        st.write(f"Dear Hiring Manager,\n\nI am writing to express my interest in the {job_title} role...\n\n[Content continues here, limited to {word_count} words].")

elif selection == "🗺️ Career Roadmap":
    st.header("🗺️ Career Roadmap")
    desired_role = st.text_input("Your Desired Role", help="e.g., Machine Learning Engineer")

    if st.button("Generate Roadmap"):
        st.write(f"## Roadmap for {desired_role}")
        st.markdown("""
        1. Learn Python, Statistics, and Linear Algebra
        2. Master ML Libraries (scikit-learn, TensorFlow)
        3. Work on real-world projects
        4. Build a portfolio
        5. Apply to internships or junior roles
        """)

elif selection == "💬 Career Chatbot":
    st.header("💬 Career Chatbot")
    query = st.text_input("Ask me anything about careers")

    if st.button("Get Answer"):
        st.success("Here’s a helpful tip from your career assistant:")
        st.write("Keep your resume concise and tailored to each job you apply for.")

# FOOTER
st.markdown("""
---
**SmartHire** - Empowering Careers with AI 🚀
""")
