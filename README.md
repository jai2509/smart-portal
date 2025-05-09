# 🚀 SmartHire: AI Job Portal

SmartHire is an intelligent job assistant powered by LLM (GROQ), Hugging Face embeddings, and Jooble API. It helps job seekers by parsing their resumes, recommending jobs, generating cover letters, and offering personalized career guidance—all through a sleek Streamlit interface.

---

## 🧠 Features

- 📄 **Resume Parsing** — Upload PDF, DOCX, or TXT and extract structured content.
- 🧠 **AI Resume Review** — Get resume improvement tips based on job role using LLaMA-3 (via GROQ API).
- 📝 **Cover Letter Generator** — Generate downloadable, professional cover letters.
- 🔍 **Job Recommendations** — Find relevant jobs using the Jooble Job API.
- 🗺️ **Career Roadmap** — Get a personalized AI-generated plan based on your background.
- 💬 **Career Chatbot** — Ask career-related questions and receive contextual answers.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend Services**: GROQ API (LLaMA3), Jooble API
- **NLP/AI**: Hugging Face Embeddings, LLaMA3-70B
- **File Handling**: PyPDF2, python-docx
- **Environment Management**: python-dotenv

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/smarthire-ai-job-portal.git
cd smarthire-ai-job-portal
```
#2. Install Dependencies
pip install -r requirements.txt
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
JOOBLE_API_KEY=your_jooble_api_key
streamlit run app.py

#📁 Project Structure
bash
Copy
Edit
├── app.py               # Main Streamlit application
├── requirements.txt     # Required Python packages
└── .env                 # API keys (not included in repo)
📸 Screenshots
![screenshot 6](https://github.com/user-attachments/assets/af6d1b29-53fc-4735-b3bc-32e575ae34a0)
![screenshot 2](https://github.com/user-attachments/assets/08c7b16f-603e-4fd8-983e-00ff5404c663)
![screenshot 3](https://github.com/user-attachments/assets/194c622f-c09a-488a-8680-ff329e2e372d)
![screenshot 4](https://github.com/user-attachments/assets/1e228fba-5248-4a9c-bdd9-53d990b7af7f)
![screenshot 5](https://github.com/user-attachments/assets/33a8e84a-27eb-4ddb-be43-ef4a99f9d433)
![screenshot 1](https://github.com/user-attachments/assets/5417d68d-5920-48a5-8f1e-43077b3a7f94)


# Roadmap
 Add resume editing

 Enable user profile & session saving

 Add email job alerts

 Enhance chatbot with memory
 
