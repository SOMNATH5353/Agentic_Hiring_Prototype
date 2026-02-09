# Agentic Hiring System - FastAPI Server

AI-powered recruitment analysis with explainable AI and RESTful API.

## Features

- 🚀 FastAPI REST API
- 📊 Candidate ranking with composite scoring
- 🔍 Explainable AI (XAI) analysis
- 🔒 PII redaction and privacy protection
- 📁 PDF report generation
- 🎯 Semantic similarity matching

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your HF_TOKEN
```

## Running the Server

```bash
# Development
python app.py

# Production
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will run at: `http://localhost:8000`

## API Endpoints

### Health Check
```bash
GET /api/v1/
```

### Upload Files
```bash
POST /api/v1/upload
Content-Type: multipart/form-data

files: [jd.pdf, resume1.pdf, resume2.pdf, ...]
```

Response:
```json
{
  "message": "Successfully uploaded 4 files",
  "session_id": "uuid-here",
  "total_files": 4
}
```

### Analyze Candidates
```bash
POST /api/v1/analyze/{session_id}
```

Response:
```json
{
  "job_description": "jd.pdf",
  "total_candidates": 3,
  "candidates": [
    {
      "name": "candidate1.pdf",
      "scores": {
        "role_fit": 0.75,
        "capability_strength": 0.68,
        "growth_potential": 0.85,
        "domain_compatibility": 0.92,
        "execution_language": 1,
        "composite_score": 0.78
      },
      "action": "SELECT_FAST_TRACK",
      "explanation": "...",
      "rank": "1",
      "tier": "Excellent"
    }
  ],
  "summary": {
    "hire": 1,
    "interview": 1,
    "pool": 1,
    "reject": 0
  }
}
```

### Download Reports
```bash
# Ranking report PDF
GET /api/v1/download/{session_id}/ranking-report

# Analysis output PDF
GET /api/v1/download/{session_id}/analysis-output

# XAI explanations (text)
GET /api/v1/download/{session_id}/xai-report
```

### Delete Session
```bash
DELETE /api/v1/session/{session_id}
```

## Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

```python
import requests

# Upload files
files = [
    ('files', open('jd.pdf', 'rb')),
    ('files', open('resume1.pdf', 'rb')),
    ('files', open('resume2.pdf', 'rb'))
]
response = requests.post('http://localhost:8000/api/v1/upload', files=files)
session_id = response.json()['session_id']

# Analyze
response = requests.post(f'http://localhost:8000/api/v1/analyze/{session_id}')
results = response.json()

# Download report
response = requests.get(
    f'http://localhost:8000/api/v1/download/{session_id}/ranking-report'
)
with open('ranking_report.pdf', 'wb') as f:
    f.write(response.content)
```

## Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t agentic-hiring .
docker run -p 8000:8000 agentic-hiring
```

## Security

- All PII is redacted before storage
- Session files are automatically cleaned up
- Use `.env` for sensitive data
- Enable authentication in production
- Configure CORS appropriately

## License

MIT License
