from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

# Association table for many-to-many relationship between contacts and tags
contact_tag_association = Table(
    'contact_tag_association',
    Base.metadata,
    Column('contact_id', Integer, ForeignKey('contacts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    address = Column(String)
    
    # Relationships
    phone_numbers = relationship("PhoneNumber", back_populates="contact", cascade="all, delete-orphan")
    addresses = relationship("Address", back_populates="contact", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=contact_tag_association, back_populates="contacts")

class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    number = Column(String, nullable=False)
    
    # Unique constraint: same phone number cannot be assigned to different contacts
    __table_args__ = (UniqueConstraint('number', name='unique_phone_number'),)
    
    contact = relationship("Contact", back_populates="phone_numbers")

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    address = Column(String, nullable=False)
    
    # Unique constraint: same address cannot be assigned to different contacts
    __table_args__ = (UniqueConstraint('address', name='unique_address'),)
    
    contact = relationship("Contact", back_populates="addresses")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    
    contacts = relationship("Contact", secondary=contact_tag_association, back_populates="tags")

