from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime

class PhoneNumberBase(BaseModel):
    number: str = Field(..., min_length=1, max_length=20)

class PhoneNumberCreate(PhoneNumberBase):
    pass

class PhoneNumberResponse(PhoneNumberBase):
    id: int
    
    class Config:
        from_attributes = True

class AddressBase(BaseModel):
    address: str = Field(..., min_length=1, max_length=500)

class AddressCreate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: int
    
    class Config:
        from_attributes = True

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    
    class Config:
        from_attributes = True

class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)

class ContactCreate(ContactBase):
    phone_numbers: Optional[List[PhoneNumberCreate]] = []
    addresses: Optional[List[AddressCreate]] = []
    tags: Optional[List[str]] = []  # Tag names

class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_numbers: Optional[List[PhoneNumberCreate]] = None
    addresses: Optional[List[AddressCreate]] = None
    tags: Optional[List[str]] = None

class ContactResponse(ContactBase):
    id: int
    phone_numbers: List[PhoneNumberResponse] = []
    addresses: List[AddressResponse] = []
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True

class ContactListResponse(BaseModel):
    contacts: List[ContactResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class SearchQuery(BaseModel):
    query: Optional[str] = None  # Substring search on name, email, phone
    tag: Optional[str] = None  # Filter by tag
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    sort_by: str = Field("name", pattern="^(name|email|created_at)$")
    sort_order: str = Field("asc", pattern="^(asc|desc)$")

