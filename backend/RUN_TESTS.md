# Running Tests

## Prerequisites

1. **Python 3.11+** (tested with Python 3.13)
2. **Virtual Environment** (recommended)

## Setup

### Option 1: Using Virtual Environment (Recommended)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using Docker

```bash
# Run tests in Docker container
docker-compose exec backend pytest
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_crud.py
pytest tests/test_api.py
```

### Run specific test
```bash
pytest tests/test_crud.py::test_create_contact
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run with minimal output
```bash
pytest -q
```

## Test Results

All 22 tests should pass:
- ✅ 9 API endpoint tests
- ✅ 13 CRUD operation tests
- ✅ Uniqueness constraint tests
- ✅ Validation tests

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: SQLAlchemy compatibility error
**Solution**: Update SQLAlchemy to version 2.0.25+:
```bash
pip install --upgrade sqlalchemy
```

### Issue: Pydantic compilation error
**Solution**: Use a virtual environment with pre-built wheels:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Test Coverage

The test suite covers:
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Search functionality (substring and tag filtering)
- ✅ Pagination and sorting
- ✅ Field validation
- ✅ Unique constraints (phone numbers and addresses)
- ✅ Error handling (404, 422)
- ✅ Duplicate names (allowed)
- ✅ Cross-field uniqueness validation

