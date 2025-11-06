import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app import models, schemas, crud

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_contact(db):
    """Test creating a contact"""
    contact_data = schemas.ContactCreate(
        name="John Doe",
        email="john@example.com",
        phone="1234567890",
        phone_numbers=[schemas.PhoneNumberCreate(number="9876543210")],
        addresses=[schemas.AddressCreate(address="123 Main St")],
        tags=["friend", "work"]
    )
    contact = crud.create_contact(db=db, contact=contact_data)
    assert contact.name == "John Doe"
    assert contact.email == "john@example.com"
    assert len(contact.phone_numbers) == 1
    assert len(contact.addresses) == 1
    assert len(contact.tags) == 2

def test_get_contact(db):
    """Test getting a contact by ID"""
    contact_data = schemas.ContactCreate(name="Jane Smith", email="jane@example.com")
    created = crud.create_contact(db=db, contact=contact_data)
    contact = crud.get_contact(db=db, contact_id=created.id)
    assert contact is not None
    assert contact.name == "Jane Smith"

def test_get_contacts_with_pagination(db):
    """Test listing contacts with pagination"""
    # Create multiple contacts
    for i in range(5):
        crud.create_contact(db=db, contact=schemas.ContactCreate(name=f"Contact {i}"))
    
    contacts, total = crud.get_contacts(db=db, skip=0, limit=2)
    assert len(contacts) == 2
    assert total == 5

def test_search_contacts_by_name(db):
    """Test searching contacts by name substring"""
    crud.create_contact(db=db, contact=schemas.ContactCreate(name="John Doe"))
    crud.create_contact(db=db, contact=schemas.ContactCreate(name="Jane Smith"))
    
    contacts, total = crud.search_contacts(db=db, query="John")
    assert total == 1
    assert contacts[0].name == "John Doe"

def test_search_contacts_by_tag(db):
    """Test filtering contacts by tag"""
    crud.create_contact(db=db, contact=schemas.ContactCreate(name="John", tags=["friend"]))
    crud.create_contact(db=db, contact=schemas.ContactCreate(name="Jane", tags=["work"]))
    
    contacts, total = crud.search_contacts(db=db, tag="friend")
    assert total == 1
    assert contacts[0].name == "John"

def test_update_contact(db):
    """Test updating a contact"""
    contact = crud.create_contact(db=db, contact=schemas.ContactCreate(name="John"))
    update_data = schemas.ContactUpdate(name="John Updated")
    updated = crud.update_contact(db=db, contact_id=contact.id, contact_update=update_data)
    assert updated.name == "John Updated"

def test_delete_contact(db):
    """Test deleting a contact"""
    contact = crud.create_contact(db=db, contact=schemas.ContactCreate(name="John"))
    success = crud.delete_contact(db=db, contact_id=contact.id)
    assert success is True
    deleted = crud.get_contact(db=db, contact_id=contact.id)
    assert deleted is None

def test_duplicate_names_allowed(db):
    """Test that multiple contacts can have the same name"""
    contact1 = crud.create_contact(db=db, contact=schemas.ContactCreate(name="John Doe"))
    contact2 = crud.create_contact(db=db, contact=schemas.ContactCreate(name="John Doe"))
    
    assert contact1.name == contact2.name
    assert contact1.id != contact2.id

def test_unique_phone_number_constraint(db):
    """Test that same phone number cannot be assigned to different contacts"""
    # Create contact with phone number in phone_numbers list
    contact1 = crud.create_contact(
        db=db,
        contact=schemas.ContactCreate(name="John", phone_numbers=[schemas.PhoneNumberCreate(number="1234567890")])
    )
    
    # Try to assign same phone number to another contact - should fail
    with pytest.raises(ValueError, match="already assigned"):
        crud.create_contact(
            db=db,
            contact=schemas.ContactCreate(name="Jane", phone_numbers=[schemas.PhoneNumberCreate(number="1234567890")])
        )

def test_unique_phone_field_constraint(db):
    """Test that Contact.phone field cannot be assigned to different contacts"""
    # Create contact with phone in Contact.phone field
    contact1 = crud.create_contact(
        db=db,
        contact=schemas.ContactCreate(name="John", phone="1234567890")
    )
    
    # Try to assign same phone to another contact - should fail
    with pytest.raises(ValueError, match="already assigned"):
        crud.create_contact(
            db=db,
            contact=schemas.ContactCreate(name="Jane", phone="1234567890")
        )

def test_unique_phone_cross_field_constraint(db):
    """Test that Contact.phone cannot conflict with PhoneNumber.number"""
    # Create contact with phone in Contact.phone field
    contact1 = crud.create_contact(
        db=db,
        contact=schemas.ContactCreate(name="John", phone="1234567890")
    )
    
    # Try to assign same phone in phone_numbers list - should fail
    with pytest.raises(ValueError, match="already assigned"):
        crud.create_contact(
            db=db,
            contact=schemas.ContactCreate(name="Jane", phone_numbers=[schemas.PhoneNumberCreate(number="1234567890")])
        )

def test_unique_address_constraint(db):
    """Test that same address cannot be assigned to different contacts"""
    contact1 = crud.create_contact(
        db=db,
        contact=schemas.ContactCreate(name="John", addresses=[schemas.AddressCreate(address="123 Main St")])
    )
    
    # Try to assign same address to another contact - should fail
    with pytest.raises(ValueError, match="already assigned"):
        crud.create_contact(
            db=db,
            contact=schemas.ContactCreate(name="Jane", addresses=[schemas.AddressCreate(address="123 Main St")])
        )

def test_update_phone_uniqueness(db):
    """Test that updating phone number checks for uniqueness"""
    contact1 = crud.create_contact(
        db=db,
        contact=schemas.ContactCreate(name="John", phone="1234567890")
    )
    contact2 = crud.create_contact(
        db=db,
        contact=schemas.ContactCreate(name="Jane", phone="9876543210")
    )
    
    # Try to update contact2 with contact1's phone - should fail
    with pytest.raises(ValueError, match="already assigned"):
        crud.update_contact(
            db=db,
            contact_id=contact2.id,
            contact_update=schemas.ContactUpdate(phone="1234567890")
        )

