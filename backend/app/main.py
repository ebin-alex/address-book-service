from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from . import crud, schemas, models
from .database import get_db, init_db

app = FastAPI(
    title="Address Book API",
    description="REST API for managing contacts",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def root():
    return {"message": "Address Book API", "docs": "/docs"}

@app.post("/contacts", response_model=schemas.ContactResponse, status_code=201)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    """Create a new contact"""
    try:
        return crud.create_contact(db=db, contact=contact)
    except ValueError as e:
        # Handle uniqueness validation errors (phone/address already exists)
        if "already assigned" in str(e).lower():
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle database constraint violations
        if "unique" in str(e).lower() or "constraint" in str(e).lower():
            raise HTTPException(
                status_code=422,
                detail=f"Phone number or address already assigned to another contact: {str(e)}"
            )
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/contacts", response_model=schemas.ContactListResponse)
def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("name", pattern="^(name|email)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """List all contacts with pagination and sorting"""
    skip = (page - 1) * page_size
    contacts, total = crud.get_contacts(
        db=db,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    total_pages = (total + page_size - 1) // page_size
    return {
        "contacts": contacts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@app.get("/contacts/search", response_model=schemas.ContactListResponse)
def search_contacts(
    query: Optional[str] = Query(None, description="Substring search on name, email, phone"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("name", pattern="^(name|email)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """Search contacts by substring and/or tag with pagination"""
    skip = (page - 1) * page_size
    contacts, total = crud.search_contacts(
        db=db,
        query=query,
        tag=tag,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    total_pages = (total + page_size - 1) // page_size
    return {
        "contacts": contacts,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@app.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """Get a contact by ID"""
    contact = crud.get_contact(db=db, contact_id=contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(
    contact_id: int,
    contact_update: schemas.ContactUpdate,
    db: Session = Depends(get_db)
):
    """Update a contact"""
    try:
        contact = crud.update_contact(db=db, contact_id=contact_id, contact_update=contact_update)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact
    except ValueError as e:
        # Handle uniqueness validation errors (phone/address already exists)
        if "already assigned" in str(e).lower():
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle database constraint violations
        if "unique" in str(e).lower() or "constraint" in str(e).lower():
            raise HTTPException(
                status_code=422,
                detail=f"Phone number or address already assigned to another contact: {str(e)}"
            )
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/contacts/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """Delete a contact"""
    success = crud.delete_contact(db=db, contact_id=contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    return None

