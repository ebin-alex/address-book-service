from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import or_, func
from typing import List, Optional
from . import models, schemas

def check_phone_number_exists(db: Session, phone_number: str, exclude_contact_id: Optional[int] = None) -> bool:
    """Check if a phone number already exists in Contact.phone or PhoneNumber.number"""
    if not phone_number:
        return False
    
    # Check if phone number exists in Contact.phone field
    query = db.query(models.Contact).filter(models.Contact.phone == phone_number)
    if exclude_contact_id:
        query = query.filter(models.Contact.id != exclude_contact_id)
    if query.first():
        return True
    
    # Check if phone number exists in PhoneNumber table
    query = db.query(models.PhoneNumber).filter(models.PhoneNumber.number == phone_number)
    if exclude_contact_id:
        query = query.filter(models.PhoneNumber.contact_id != exclude_contact_id)
    if query.first():
        return True
    
    return False

def check_address_exists(db: Session, address: str, exclude_contact_id: Optional[int] = None) -> bool:
    """Check if an address already exists in Contact.address or Address.address"""
    if not address:
        return False
    
    # Check if address exists in Contact.address field
    query = db.query(models.Contact).filter(models.Contact.address == address)
    if exclude_contact_id:
        query = query.filter(models.Contact.id != exclude_contact_id)
    if query.first():
        return True
    
    # Check if address exists in Address table
    query = db.query(models.Address).filter(models.Address.address == address)
    if exclude_contact_id:
        query = query.filter(models.Address.contact_id != exclude_contact_id)
    if query.first():
        return True
    
    return False

def create_contact(db: Session, contact: schemas.ContactCreate) -> models.Contact:
    """Create a new contact with phone numbers, addresses, and tags"""
    # Check if the phone field conflicts with existing phone numbers
    if contact.phone:
        if check_phone_number_exists(db, contact.phone):
            raise ValueError(f"Phone number '{contact.phone}' is already assigned to another contact")
    
    # Check if phone numbers in the list conflict with existing ones
    for phone_data in contact.phone_numbers or []:
        if check_phone_number_exists(db, phone_data.number):
            raise ValueError(f"Phone number '{phone_data.number}' is already assigned to another contact")
    
    # Check if addresses in the list conflict with existing ones
    for address_data in contact.addresses or []:
        if check_address_exists(db, address_data.address):
            raise ValueError(f"Address '{address_data.address}' is already assigned to another contact")
    
    db_contact = models.Contact(
        name=contact.name,
        email=contact.email,
        phone=contact.phone
    )
    db.add(db_contact)
    db.flush()  # Get the ID without committing
    
    # Add phone numbers
    for phone_data in contact.phone_numbers or []:
        db_phone = models.PhoneNumber(contact_id=db_contact.id, number=phone_data.number)
        db.add(db_phone)
    
    # Add addresses
    for address_data in contact.addresses or []:
        db_address = models.Address(contact_id=db_contact.id, address=address_data.address)
        db.add(db_address)
    
    # Add tags
    if contact.tags:
        for tag_name in contact.tags:
            db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name.lower()).first()
            if not db_tag:
                db_tag = models.Tag(name=tag_name.lower())
                db.add(db_tag)
            db_contact.tags.append(db_tag)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contact(db: Session, contact_id: int) -> Optional[models.Contact]:
    """Get a contact by ID"""
    return db.query(models.Contact).options(
        joinedload(models.Contact.phone_numbers),
        joinedload(models.Contact.addresses),
        joinedload(models.Contact.tags)
    ).filter(models.Contact.id == contact_id).first()

def get_contacts(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "name",
    sort_order: str = "asc"
) -> tuple[List[models.Contact], int]:
    """Get all contacts with pagination and sorting"""
    query = db.query(models.Contact).options(
        joinedload(models.Contact.phone_numbers),
        joinedload(models.Contact.addresses),
        joinedload(models.Contact.tags)
    )
    
    # Sorting
    sort_column = getattr(models.Contact, sort_by, models.Contact.name)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)
    
    total = query.count()
    contacts = query.offset(skip).limit(limit).all()
    return contacts, total

def search_contacts(
    db: Session,
    query: Optional[str] = None,
    tag: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "name",
    sort_order: str = "asc"
) -> tuple[List[models.Contact], int]:
    """Search contacts by substring (name, email, phone) and/or tag"""
    db_query = db.query(models.Contact)
    
    # Substring search on name, email, phone
    if query:
        search_term = f"%{query.lower()}%"
        phone_alias = aliased(models.PhoneNumber)
        db_query = db_query.outerjoin(phone_alias, models.Contact.id == phone_alias.contact_id).filter(
            or_(
                func.lower(models.Contact.name).like(search_term),
                func.lower(models.Contact.email).like(search_term),
                func.lower(models.Contact.phone).like(search_term),
                func.lower(phone_alias.number).like(search_term),
            )
        )
    
    # Filter by tag
    if tag:
        tag_alias = aliased(models.Tag)
        db_query = db_query.join(tag_alias, models.Contact.tags).filter(
            func.lower(tag_alias.name) == tag.lower()
        )
    
    # Sorting
    sort_column = getattr(models.Contact, sort_by, models.Contact.name)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    db_query = db_query.options(
        joinedload(models.Contact.phone_numbers),
        joinedload(models.Contact.addresses),
        joinedload(models.Contact.tags)
    ).order_by(sort_column).distinct()
    
    total = db_query.count()
    contacts = db_query.offset(skip).limit(limit).all()
    return contacts, total

def update_contact(
    db: Session,
    contact_id: int,
    contact_update: schemas.ContactUpdate
) -> Optional[models.Contact]:
    """Update a contact"""
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return None
    
    # Update basic fields
    if contact_update.name is not None:
        db_contact.name = contact_update.name
    if contact_update.email is not None:
        db_contact.email = contact_update.email
    
    # Check phone number uniqueness before updating
    if contact_update.phone is not None:
        if check_phone_number_exists(db, contact_update.phone, exclude_contact_id=contact_id):
            raise ValueError(f"Phone number '{contact_update.phone}' is already assigned to another contact")
        db_contact.phone = contact_update.phone
    
    # Update phone numbers if provided
    if contact_update.phone_numbers is not None:
        # Check uniqueness before deleting existing ones
        for phone_data in contact_update.phone_numbers:
            if check_phone_number_exists(db, phone_data.number, exclude_contact_id=contact_id):
                raise ValueError(f"Phone number '{phone_data.number}' is already assigned to another contact")
        
        # Delete existing phone numbers
        db.query(models.PhoneNumber).filter(models.PhoneNumber.contact_id == contact_id).delete()
        # Add new phone numbers
        for phone_data in contact_update.phone_numbers:
            db_phone = models.PhoneNumber(contact_id=contact_id, number=phone_data.number)
            db.add(db_phone)
    
    # Update addresses if provided
    if contact_update.addresses is not None:
        # Check uniqueness before deleting existing ones
        for address_data in contact_update.addresses:
            if check_address_exists(db, address_data.address, exclude_contact_id=contact_id):
                raise ValueError(f"Address '{address_data.address}' is already assigned to another contact")
        
        # Delete existing addresses
        db.query(models.Address).filter(models.Address.contact_id == contact_id).delete()
        # Add new addresses
        for address_data in contact_update.addresses:
            db_address = models.Address(contact_id=contact_id, address=address_data.address)
            db.add(db_address)
    
    # Update tags if provided
    if contact_update.tags is not None:
        db_contact.tags.clear()
        for tag_name in contact_update.tags:
            db_tag = db.query(models.Tag).filter(models.Tag.name == tag_name.lower()).first()
            if not db_tag:
                db_tag = models.Tag(name=tag_name.lower())
                db.add(db_tag)
            db_contact.tags.append(db_tag)
    
    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int) -> bool:
    """Delete a contact"""
    db_contact = get_contact(db, contact_id)
    if not db_contact:
        return False
    db.delete(db_contact)
    db.commit()
    return True

