# AI Codebase Q&A Assistant - Backend (Vectorless RAG)

This is the backend service for an AI-powered codebase assistant that allows users to understand and query any GitHub repository using natural language.

It is built using FastAPI and implements a **vectorless RAG (Retrieval-Augmented Generation)** approach.

---

## 🚀 Overview

The backend handles:
- Repository cloning  
- Codebase analysis  
- File summarization  
- Smart file retrieval  
- Context-aware chat  

Instead of embeddings, it uses:
- keyword-based scoring  
- file description matching  
- prompt-based reasoning  

---

## 🧠 Core Idea

A **vectorless RAG system** that retrieves relevant files without using vector databases.

This makes the system:
- lightweight  
- easier to debug  
- cost-efficient  

---

## ⚙️ Tech Stack

- FastAPI  
- Python  
- OpenRouter API (LLM)  
- GitPython  

---

## 🔍 How It Works

### 1. Load Repository
- Clones GitHub repo locally

### 2. Analyze Codebase
- Extracts file structure  
- Generates file descriptions  
- Creates project summary  

### 3. Retrieval
- Scores files based on query  
- Selects top relevant files  
- Injects code into prompt  

### 4. Chat System
- Uses conversation memory  
- Handles follow-up questions  
- Returns structured answers + code  

---

## 📡 API Endpoints

### Load Repository

POST /load


### Analyze Repository

POST /analyze


### Chat with Codebase

POST /chat


---

## ⚡ Installation

```bash
git clone <your-backend-repo>
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
☁️ Deployment

Can be deployed on:

AWS EC2 (recommended)
AWS Lambda + API Gateway
💡 Use Cases
Understanding unfamiliar codebases
Developer onboarding
Debugging and code exploration
Internal developer tools
⚠️ Limitations
No semantic embeddings
Performance depends on keyword matching
Limited on very large repositories
🔮 Future Improvements
Add vector database (FAISS / Chroma)
Hybrid retrieval system
Better multi-file reasoning
📌 Key Concept

This project demonstrates how a vectorless RAG pipeline can power an AI code assistant without using embeddings.
