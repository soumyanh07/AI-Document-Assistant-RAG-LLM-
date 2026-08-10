# 📄 AI Document Assistant (RAG + LLM)

> An AI-powered document assistant that lets users upload documents and interact with them conversationally using Retrieval-Augmented Generation (RAG) and Large Language Models.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Overview

AI Document Assistant lets users upload documents (PDF, text, etc.), automatically parses and embeds their content, and enables natural-language conversations grounded in that content using RAG. Instead of relying purely on an LLM's general knowledge, the assistant retrieves relevant document chunks and uses them as context — reducing hallucination and keeping answers grounded in the source material.

<!-- TODO: 2-3 sentences on the specific problem this solves / why you built it -->

---

## ✨ Features

<!-- TODO: check each box based on what's actually implemented -->

- [ ] Document upload & parsing (PDF / text)
- [ ] Text chunking & embedding generation
- [ ] Vector similarity search
- [ ] Conversational chat over document content (RAG)
- [ ] JWT-based authentication
- [ ] Chat history / session management
- [ ] Multi-document support
- [ ] Dockerized deployment
- [ ] CI/CD via GitHub Actions
- [ ] Infrastructure as code (Terraform)

---

## 🏗 Architecture

```
 User
  │
  ▼
 Frontend (React)
  │
  ▼
 Backend API (FastAPI)
  │
  ├── Auth Service (JWT)
  ├── Parser (document ingestion)
  ├── Embeddings (chunking + vectorization)
  ├── RAG Engine (retrieval + prompt construction)
  └── Chat Service
       │
       ▼
     Vector Database
       │
       ▼
     LLM Provider
```

---

## 🛠 Tech Stack

**Backend**
- Python 3.12
- FastAPI
- SQLAlchemy <!-- TODO: confirm ORM/DB layer used -->
- <!-- TODO: vector DB (e.g. ChromaDB, Pinecone, FAISS) -->

**Frontend**
- React
- <!-- TODO: TypeScript? Tailwind? Vite? -->

**AI**
- <!-- TODO: LLM provider (OpenAI, Gemini, local model?) -->
- LangChain <!-- TODO: confirm -->
- RAG / Embeddings

**DevOps**
- Docker
- Terraform
- GitHub Actions

---

## 📂 Project Structure

```
AI-Document-Assistant/
│
├── backend/
│   └── app/
│       ├── api/          # Route handlers
│       ├── auth/         # Authentication logic
│       ├── chat/         # Chat session handling
│       ├── embeddings/   # Embedding generation
│       ├── parser/       # Document parsing/ingestion
│       ├── rag/          # Retrieval-augmented generation logic
│       ├── database/     # DB models & connection
│       ├── models/       # Pydantic / data models
│       ├── services/     # Business logic
│       └── utils/        # Shared helpers
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       ├── context/
│       └── api/
│
├── docker/                # Docker configs
├── terraform/              # Infra as code
├── .github/workflows/       # CI/CD pipelines
└── tests/                  # Test suite
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js <!-- TODO: version -->
- Docker (optional, for containerized run)
- <!-- TODO: API keys needed, e.g. OpenAI API key -->

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/soumyanh07/AI-Document-Assistant-RAG-LLM-.git
cd AI-Document-Assistant-RAG-LLM-

# Install dependencies
pip install -r requirements_mine.txt

# Run the backend
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create a `.env` file with:
```
DATABASE_URL=
LLM_API_KEY=
VECTOR_DB_URL=
```
<!-- TODO: replace with your actual required env vars -->

### Run with Docker

```bash
docker-compose up --build
```
<!-- TODO: confirm this matches your docker/ setup -->

---

## 🎯 Roadmap

<!-- TODO: fill in what's done vs planned, e.g.: -->

| Module | Status |
|---|---|
| Backend scaffold | ✅ Completed |
| Document parsing | 🚧 In Progress |
| Embedding pipeline | ⏳ Planned |
| RAG chat | ⏳ Planned |
| Auth | ⏳ Planned |
| Docker deployment | ⏳ Planned |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to fork the repository and submit a pull request.

---

## 👨‍💻 Author

**Soumya**
AI & Machine Learning Undergraduate

📧 soumyanh7@gmail.com
GitHub: [@soumyanh07](https://github.com/soumyanh07)

---

## 📜 License

This project is licensed under the MIT License.
