# Address Book Service

A full-stack address book application with REST API backend and minimal frontend UI for managing contacts.

## Features

- **CRUD Operations**: Create, Read, Update, Delete contacts
- **Multiple Phone Numbers & Addresses**: Add multiple phone numbers and addresses per contact
- **Tags/Labels**: Organize contacts with tags
- **Search**: Substring search on name, email, and phone numbers
- **Tag Filtering**: Filter contacts by tags
- **Pagination & Sorting**: List contacts with pagination and sorting options
- **Field Validation**: Proper validation with appropriate HTTP status codes (400/404/422)
- **Unique Constraints**: Same phone number or address cannot be assigned to different contacts
- **Tests**: Comprehensive unit tests for core logic and API endpoints

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (can be easily swapped for PostgreSQL)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Testing**: pytest
- **Containerization**: Docker & Docker Compose

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py         # SQLAlchemy database models
│   │   ├── schemas.py        # Pydantic schemas for validation
│   │   ├── crud.py           # Business logic / CRUD operations
│   │   └── database.py       # Database configuration
│   ├── tests/
│   │   ├── test_crud.py      # Unit tests for CRUD operations
│   │   └── test_api.py       # API endpoint tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── docker-compose.yml
└── README.md
```

## Design Decisions

### Database Schema

- **Contacts Table**: Stores basic contact information (name, email, phone)
- **Phone Numbers Table**: Separate table for multiple phone numbers with unique constraint
- **Addresses Table**: Separate table for multiple addresses with unique constraint
- **Tags Table**: Many-to-many relationship with contacts for flexible tagging

### API Design

- RESTful API with standard HTTP methods (GET, POST, PUT, DELETE)
- Consistent JSON response format
- Proper HTTP status codes:
  - `201` for successful creation
  - `200` for successful retrieval/update
  - `204` for successful deletion
  - `400` for bad requests
  - `404` for not found
  - `422` for validation errors and constraint violations

### Search Implementation

- Substring search on name, email, and phone fields using SQL LIKE
- Case-insensitive search
- Tag filtering using JOIN operations
- Combined search and tag filtering supported

### Validation

- Pydantic schemas for request validation
- Email validation using EmailStr
- Field length constraints
- Required field validation

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (optional, for containerized setup)

### Option 1: Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd address-book-service
```

2. Start the services:
```bash
docker-compose up
```

3. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

#### Frontend Setup

1. Serve the frontend using a simple HTTP server:
```bash
cd frontend
python -m http.server 8080
```

Or use any other static file server. The frontend will be available at http://localhost:8080

**Note**: You may need to update the `API_BASE_URL` in `frontend/app.js` if your backend is running on a different port.

## Running Tests

### Backend Tests

1. Navigate to backend directory:
```bash
cd backend
```

2. Run tests:
```bash
pytest
```

3. Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Test Coverage

The test suite includes:
- Unit tests for CRUD operations (`test_crud.py`)
- API endpoint tests (`test_api.py`)
- Validation tests
- Constraint violation tests (unique phone/address)

## API Endpoints

### Contacts

- `GET /contacts` - List all contacts (with pagination and sorting)
  - Query params: `page`, `page_size`, `sort_by`, `sort_order`
  
- `POST /contacts` - Create a new contact
  - Body: JSON with contact data

- `GET /contacts/{contact_id}` - Get a specific contact

- `PUT /contacts/{contact_id}` - Update a contact

- `DELETE /contacts/{contact_id}` - Delete a contact

### Search

- `GET /contacts/search` - Search contacts
  - Query params: `query` (substring search), `tag` (filter by tag), `page`, `page_size`, `sort_by`, `sort_order`

## Example API Usage

### Create a Contact
```bash
curl -X POST http://localhost:8000/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "phone_numbers": [{"number": "9876543210"}],
    "addresses": [{"address": "123 Main St"}],
    "tags": ["friend", "work"]
  }'
```

### Search Contacts
```bash
curl "http://localhost:8000/contacts/search?query=John&tag=friend&page=1&page_size=10"
```

### List Contacts
```bash
curl "http://localhost:8000/contacts?page=1&page_size=10&sort_by=name&sort_order=asc"
```

## Trade-offs

### SQLite vs PostgreSQL

- **Current**: SQLite for simplicity and zero-configuration
- **Trade-off**: SQLite doesn't support concurrent writes well, but sufficient for this use case
- **Migration**: Can easily switch to PostgreSQL by changing `DATABASE_URL` in `database.py`

### In-Memory Search vs Full-Text Search

- **Current**: SQL LIKE queries for substring matching
- **Trade-off**: Simple but may be slower on large datasets
- **Alternative**: Could use full-text search (PostgreSQL FTS, Elasticsearch) for better performance

### Frontend Framework

- **Current**: Vanilla JavaScript for minimal dependencies
- **Trade-off**: More code but no build process needed
- **Alternative**: React/Vue would provide better organization for larger applications

### Authentication

- **Current**: Not implemented (nice-to-have)
- **Trade-off**: Simpler for demo, but production would need authentication
- **Implementation**: Could add JWT tokens or API keys

## Future Enhancements

- [ ] Authentication and authorization
- [ ] PostgreSQL support with docker-compose
- [ ] Full-text search for better performance
- [ ] Contact import/export (CSV, vCard)
- [ ] Contact groups
- [ ] Advanced filtering (date ranges, multiple tags)
- [ ] API rate limiting
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Deployment to cloud platform (AWS, Heroku, etc.)

## License

This project is open source and available under the MIT License.

