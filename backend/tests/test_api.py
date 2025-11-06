import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app import models

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """Create a test client with fresh database"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_create_contact(client):
    """Test POST /contacts"""
    response = client.post(
        "/contacts",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "phone_numbers": [{"number": "9876543210"}],
            "addresses": [{"address": "123 Main St"}],
            "tags": ["friend"]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"

def test_get_contact(client):
    """Test GET /contacts/{contact_id}"""
    # Create a contact first
    create_response = client.post("/contacts", json={"name": "Jane Smith"})
    contact_id = create_response.json()["id"]
    
    # Get the contact
    response = client.get(f"/contacts/{contact_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Smith"

def test_get_contact_not_found(client):
    """Test GET /contacts/{contact_id} with non-existent ID"""
    response = client.get("/contacts/999")
    assert response.status_code == 404

def test_list_contacts(client):
    """Test GET /contacts with pagination"""
    # Create multiple contacts
    for i in range(3):
        client.post("/contacts", json={"name": f"Contact {i}"})
    
    response = client.get("/contacts?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["contacts"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1

def test_search_contacts(client):
    """Test GET /contacts/search"""
    client.post("/contacts", json={"name": "John Doe", "email": "john@example.com"})
    client.post("/contacts", json={"name": "Jane Smith", "email": "jane@example.com"})
    
    response = client.get("/contacts/search?query=John")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "John" in data["contacts"][0]["name"]

def test_update_contact(client):
    """Test PUT /contacts/{contact_id}"""
    create_response = client.post("/contacts", json={"name": "John"})
    contact_id = create_response.json()["id"]
    
    response = client.put(
        f"/contacts/{contact_id}",
        json={"name": "John Updated"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "John Updated"

def test_delete_contact(client):
    """Test DELETE /contacts/{contact_id}"""
    create_response = client.post("/contacts", json={"name": "John"})
    contact_id = create_response.json()["id"]
    
    response = client.delete(f"/contacts/{contact_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/contacts/{contact_id}")
    assert get_response.status_code == 404

def test_validation_error(client):
    """Test validation with invalid data"""
    response = client.post("/contacts", json={"name": ""})  # Empty name
    assert response.status_code == 422  # Validation error

def test_invalid_email(client):
    """Test email validation"""
    response = client.post("/contacts", json={"name": "John", "email": "invalid-email"})
    assert response.status_code == 422

