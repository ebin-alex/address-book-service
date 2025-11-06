# Quick Start Guide

Get up and running with the Address Book Service in 5 minutes!

## Option 1: Docker (Recommended - Easiest)

```bash
# Start everything
docker-compose up

# Access:
# - Frontend: http://localhost
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

That's it! Everything is running.

## Option 2: Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Backend runs at: http://localhost:8000

### Frontend

```bash
cd frontend
python -m http.server 8080
```

Frontend runs at: http://localhost:8080

**Note**: Update `API_BASE_URL` in `frontend/app.js` if backend is on different port.

## Run Tests

```bash
cd backend
pytest
```

## First Steps

1. Open http://localhost:8000/docs (or http://localhost if using Docker)
2. Try creating a contact via the API docs
3. Or use the frontend UI at http://localhost (or http://localhost:8080)

## Example API Request

```bash
curl -X POST http://localhost:8000/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "tags": ["friend"]
  }'
```

See README.md for full documentation!

