# DocMind 📚

DocMind is an AI-powered enterprise search platform that enables intelligent document search using semantic search, hybrid retrieval, and Large Language Models.

The application provides scalable backend services for document ingestion, indexing, metadata management, and AI-powered search.

---

## Features

- AI-powered semantic search
- Hybrid retrieval (BM25 + LLM)
- Document ingestion
- Metadata management
- REST APIs
- Intelligent indexing
- Authentication
- Dockerized deployment
- Scalable backend architecture

---

## Tech Stack

### Backend

- Python
- FastAPI

### Database

- PostgreSQL
- Redis

### AI

- LangChain
- Google Gemini
- BM25
- Vector Search

### DevOps

- Docker
- Git
- GitHub

---

## Architecture

```
              User
               |
        REST API Requests
               |
         FastAPI Backend
               |
    -------------------------
    |          |            |
PostgreSQL   Redis     AI Engine
                           |
                  LangChain + Gemini
                           |
                 Hybrid Search Engine
```

---

## Project Structure

```
DocMind/
│
├── app/
│
├── api/
│
├── services/
│
├── models/
│
├── database/
│
├── tests/
│
├── docs/
│
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/sejalP07/DocMind.git
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
uvicorn app.main:app --reload
```

---

## API Overview

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | /documents | Upload Document |
| GET | /documents | List Documents |
| GET | /search | Semantic Search |
| DELETE | /documents/{id} | Delete Document |
| GET | /health | Health Check |

---

## Software Engineering Practices

- Software Design
- REST API Development
- Coding Standards
- Software Testing
- Unit Testing
- Integration Testing
- Documentation
- Version Control
- Agile Development

---

## Future Enhancements

- OCR Support
- PDF Parsing
- Multi-language Search
- Kubernetes Deployment
- AI Chat over Documents
- Cloud Storage Integration

---

## Author

**Sejal P**

Software Engineer | Backend Developer | AI Enthusiast
