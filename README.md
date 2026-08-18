# 📄 Document Analyzer API

A Django REST API that accepts documents (PDF, DOCX, TXT), extracts text, and uses an LLM to return structured summaries.

Built for: **DTP Labs — Python & AI Backend Engineer Technical Assessment**

---

## 🚀 Tech Stack

- **Backend:** Django + Django REST Framework
- **LLM:** Groq API (openai/gpt-oss-120b)
- **Task Queue:** Celery + Redis
- **Text Extraction:** PyMuPDF, python-docx
- **Containerization:** Docker + Docker Compose

---

## ⚙️ Setup Instructions

### Option 1 — Local Setup

**1. Clone the repository:**
```bash
git clone https://github.com/shubhamkummarrr/dtp-assignment.git
cd dtp-assignment


```

**2. Virtual environment banao:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

**3. Dependencies install karo:**
```bash
pip install -r requirements.txt
```

**4. Environment variables setup karo:**
```bash
cp .env.example .env
# .env file mein apni values daalo
```

**5. Database migrate karo:**
```bash
python manage.py migrate
```

**6. Redis start karo:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**7. Celery worker start karo:**
```bash
celery -A dtp_assignment worker --loglevel=info -P solo
```

**8. Django server start karo:**
```bash
python manage.py runserver
```

---

### Option 2 — Docker Setup

```bash
cp .env.example .env
# .env file mein apni values daalo

docker-compose up --build
```

---

## 🔑 Environment Variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-xxx` |
| `DEBUG` | Debug mode | `True` |
| `GROQ_API_KEY` | Groq API key | `gsk_xxx` |
| `CELERY_BROKER_URL` | Redis broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis result backend | `redis://localhost:6379/0` |

---

## 📡 API Endpoints

### 1. Upload Document
POST /api/documents/upload/
Content-Type: multipart/form-data

Body:
file: <PDF/DOCX/TXT file>


**Response:**
```json
{
    "message": "File uploaded successfully. Processing started.",
    "document_id": 1,
    "file_name": "document.pdf",
    "status": "pending"
}
```

---

### 2. List All Documents

GET /api/documents/


**Response:**
```json
{
    "count": 2,
    "documents": [
        {
            "id": 1,
            "file_name": "document.pdf",
            "file_type": "pdf",
            "status": "completed",
            "title": "Document Title",
            "language": "English",
            "word_count": 389,
            "created_at": "2026-08-17T15:22:36Z"
        }
    ]
}
```

---

### 3. Get Document Detail

GET /api/documents/<id>/


**Response:**
```json
{
    "id": 1,
    "file_name": "document.pdf",
    "file_type": "pdf",
    "status": "completed",
    "title": "Document Title",
    "summary": "This document is about...",
    "keywords": ["keyword1", "keyword2"],
    "language": "English",
    "word_count": 389,
    "extracted_text": "Full extracted text...",
    "created_at": "2026-08-17T15:22:36Z",
    "updated_at": "2026-08-17T15:22:45Z"
}
```

---

### 4. Check Document Status

GET /api/documents/<id>/status/


**Response:**
```json
{
    "document_id": 1,
    "file_name": "document.pdf",
    "status": "completed",
    "error_message": null,
    "updated_at": "2026-08-17T15:22:45Z"
}
```

---

## 🔄 Processing Flow

Upload File → Save to DB (pending)
→ Celery Task Queue
→ Extract Text (PyMuPDF/python-docx)
→ Send to Groq LLM
→ Parse JSON Response
→ Save to DB (completed)


---

## ❌ Error Handling

| Scenario | HTTP Status | Response |
|---|---|---|
| Invalid file type | 400 | `{"error": "Unsupported file type"}` |
| File too large (>10MB) | 400 | `{"error": "File too large"}` |
| No file provided | 400 | `{"error": "No file provided"}` |
| Document not found | 404 | `{"detail": "Not found"}` |
| LLM API failure | Task retry | Status: `failed` |

---

## 🎁 Bonus Features Implemented

- ✅ **Celery Background Processing** — Async document processing
- ✅ **Docker Support** — Dockerfile + docker-compose.yml

  ## ⚠️ Important Notes
- Groq API free key required: https://console.groq.com
- Model used: `allam-2-7b` 
- Free tier TPM limit: documents are processed one at a time
