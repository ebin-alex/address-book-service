# Testing Guide

This guide explains how to test the Address Book Service comprehensively.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Running Tests](#running-tests)
3. [Testing Scenarios](#testing-scenarios)
4. [API Testing](#api-testing)
5. [Frontend Testing](#frontend-testing)
6. [Integration Testing](#integration-testing)

## Prerequisites

1. **Install Dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Ensure Backend is Running** (for manual testing):
```bash
cd backend
uvicorn app.main:app --reload
```

## Running Tests

### Automated Unit Tests

Run all tests:
```bash
cd backend
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_crud.py
pytest tests/test_api.py
```

Run specific test:
```bash
pytest tests/test_crud.py::test_create_contact
```

### Test Coverage

The test suite covers:
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Search functionality
- ✅ Tag filtering
- ✅ Pagination and sorting
- ✅ Validation errors
- ✅ Unique constraints (phone/address)
- ✅ Error handling (404, 422, etc.)

## Testing Scenarios

### 1. Create Contact Tests

**Test**: Creating a contact with all fields
```bash
# Using curl
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

**Expected**: 201 Created with contact data

**Test**: Creating contact with duplicate phone number
```bash
curl -X POST http://localhost:8000/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "phone_numbers": [{"number": "1234567890"}]
  }'
```

**Expected**: 422 Unprocessable Entity (phone already exists)

### 2. Read Contact Tests

**Test**: Get all contacts
```bash
curl http://localhost:8000/contacts?page=1&page_size=10
```

**Expected**: 200 OK with paginated list

**Test**: Get contact by ID
```bash
curl http://localhost:8000/contacts/1
```

**Expected**: 200 OK with contact data

**Test**: Get non-existent contact
```bash
curl http://localhost:8000/contacts/999
```

**Expected**: 404 Not Found

### 3. Update Contact Tests

**Test**: Update contact
```bash
curl -X PUT http://localhost:8000/contacts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated",
    "email": "john.updated@example.com"
  }'
```

**Expected**: 200 OK with updated contact

**Test**: Update non-existent contact
```bash
curl -X PUT http://localhost:8000/contacts/999 \
  -H "Content-Type: application/json" \
  -d '{"name": "Test"}'
```

**Expected**: 404 Not Found

### 4. Delete Contact Tests

**Test**: Delete contact
```bash
curl -X DELETE http://localhost:8000/contacts/1
```

**Expected**: 204 No Content

**Test**: Delete non-existent contact
```bash
curl -X DELETE http://localhost:8000/contacts/999
```

**Expected**: 404 Not Found

### 5. Search Tests

**Test**: Search by name substring
```bash
curl "http://localhost:8000/contacts/search?query=John"
```

**Expected**: 200 OK with matching contacts

**Test**: Search by email substring
```bash
curl "http://localhost:8000/contacts/search?query=example.com"
```

**Expected**: 200 OK with matching contacts

**Test**: Filter by tag
```bash
curl "http://localhost:8000/contacts/search?tag=friend"
```

**Expected**: 200 OK with contacts having "friend" tag

**Test**: Combined search and tag filter
```bash
curl "http://localhost:8000/contacts/search?query=John&tag=friend"
```

**Expected**: 200 OK with contacts matching both criteria

### 6. Validation Tests

**Test**: Invalid email format
```bash
curl -X POST http://localhost:8000/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "email": "invalid-email"
  }'
```

**Expected**: 422 Validation Error

**Test**: Empty name
```bash
curl -X POST http://localhost:8000/contacts \
  -H "Content-Type: application/json" \
  -d '{"name": ""}'
```

**Expected**: 422 Validation Error

## API Testing

### Using Postman/Insomnia

1. **Import Collection**: You can create a Postman collection with these endpoints:
   - POST `/contacts` - Create contact
   - GET `/contacts` - List contacts
   - GET `/contacts/{id}` - Get contact
   - PUT `/contacts/{id}` - Update contact
   - DELETE `/contacts/{id}` - Delete contact
   - GET `/contacts/search` - Search contacts

2. **Environment Variables**:
   - `base_url`: `http://localhost:8000`

### Using HTTPie

Install HTTPie:
```bash
pip install httpie
```

Test requests:
```bash
# Create
http POST localhost:8000/contacts name="John" email="john@example.com"

# List
http GET localhost:8000/contacts

# Search
http GET localhost:8000/contacts/search query==John

# Update
http PUT localhost:8000/contacts/1 name="John Updated"

# Delete
http DELETE localhost:8000/contacts/1
```

## Frontend Testing

### Manual Testing

1. **Start Services**:
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend (using Python HTTP server)
cd frontend
python -m http.server 8080
```

2. **Open Browser**: http://localhost:8080

3. **Test Scenarios**:
   - ✅ Create new contact
   - ✅ Edit existing contact
   - ✅ Delete contact
   - ✅ Search by name/email/phone
   - ✅ Filter by tag
   - ✅ Pagination (next/previous)
   - ✅ Change page size
   - ✅ Multiple phone numbers per contact
   - ✅ Multiple addresses per contact
   - ✅ Multiple tags per contact

### Browser Console Testing

Open browser console (F12) and test:

```javascript
// Test API directly
fetch('http://localhost:8000/contacts')
  .then(r => r.json())
  .then(console.log);

// Create contact
fetch('http://localhost:8000/contacts', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'Test User',
    email: 'test@example.com',
    tags: ['test']
  })
})
  .then(r => r.json())
  .then(console.log);
```

## Integration Testing

### Docker Compose Testing

1. **Start all services**:
```bash
docker-compose up -d
```

2. **Check services**:
```bash
docker-compose ps
```

3. **View logs**:
```bash
docker-compose logs backend
docker-compose logs frontend
```

4. **Test endpoints**:
```bash
curl http://localhost:8000/
curl http://localhost:8000/docs  # API documentation
```

5. **Run tests in container**:
```bash
docker-compose exec backend pytest
```

### Database Testing

Test unique constraints:
```bash
# Create contact 1 with phone
curl -X POST http://localhost:8000/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Contact 1",
    "phone_numbers": [{"number": "1234567890"}]
  }'

# Try to create contact 2 with same phone (should fail)
curl -X POST http://localhost:8000/contacts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Contact 2",
    "phone_numbers": [{"number": "1234567890"}]
  }'
```

## Performance Testing

### Load Testing (Optional)

Using Apache Bench:
```bash
# Install ab (Apache Bench)
# On Ubuntu: sudo apt-get install apache2-utils
# On macOS: brew install httpd

# Test GET endpoint
ab -n 1000 -c 10 http://localhost:8000/contacts

# Test POST endpoint
ab -n 100 -c 5 -p contact.json -T application/json http://localhost:8000/contacts
```

## Troubleshooting

### Common Issues

1. **Database locked**: Restart backend or delete `addressbook.db`
2. **Port already in use**: Change port in `main.py` or docker-compose.yml
3. **CORS errors**: Check CORS settings in `main.py`
4. **Import errors**: Ensure you're in the correct directory and virtual environment is activated

### Debug Mode

Run backend in debug mode:
```bash
uvicorn app.main:app --reload --log-level debug
```

## Next Steps

For production testing, consider:
- [ ] Load testing with tools like Locust
- [ ] E2E testing with Selenium/Playwright
- [ ] API contract testing with Pact
- [ ] Security testing with OWASP ZAP
- [ ] Performance profiling

