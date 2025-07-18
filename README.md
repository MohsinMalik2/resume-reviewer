# 📄 Auto Screener Agent

**Auto Screener Agent** is a domain-specific AI tool designed for the recruitment industry.  
It automates the entire resume screening workflow — from parsing resumes and matching them to a job description, to shortlisting top candidates and drafting polite rejection emails for the rest — all with a single click.

---

## 🚀 Features

- ✅ **User Authentication** — Simple, secure Sign Up & Sign In flow.
- ✅ **Interactive Dashboard** — Clean dashboard with service tiles for quick access.
- ✅ **Resume & JD Upload** — Upload multiple resumes and a job description in seconds.
- ✅ **AI-Powered Parsing & Scoring** — Uses LLMs to extract candidate data and calculate fit scores.
- ✅ **Automated Shortlisting** — Ranks and shortlists top candidates automatically.
- ✅ **Rejection Drafting** — Generates ready-to-send, polite rejection emails.
- ✅ **Results Dashboard** — View shortlisted candidates, scores, and export results.

---

## 🗂️ Tech Stack

- **Frontend:** React + TypeScript  
- **Backend:** Python + FastAPI  
- **Authentication & Hosting:** Firebase  
- **AI Services:** Gemini API  
- **Parsing & File Handling:** Python libraries (e.g., pdfminer, docx)  
- **Workflow:** REST API approach

---

## 🔁 User Flow

1️⃣ **Sign Up / Sign In**  
2️⃣ **Access Dashboard** — Choose services.  
3️⃣ **Upload JD & Resumes**  
4️⃣ **Run Screening Process**  
5️⃣ **View Shortlist & Rejection Drafts**  
6️⃣ **Export Results**

---

## ⚡ Getting Started


   ```bash
    git clone https://github.com/yourusername/auto-screener-agent.git
    cd auto-screener-agent
    npm install
    npm run dev

    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    # Configure your Firebase and Gemini credentials
    python run.py


