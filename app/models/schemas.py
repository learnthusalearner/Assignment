from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import List, Optional, Dict

class Product(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    price: Optional[str] = None
    url: Optional[HttpUrl] = None
    image: Optional[HttpUrl] = None
    available: Optional[bool] = None

class Policy(BaseModel):
    url: Optional[HttpUrl] = None
    text: Optional[str] = None

class FAQ(BaseModel):
    question: str
    answer: str
    url: Optional[HttpUrl] = None

class SocialHandle(BaseModel):
    instagram: Optional[HttpUrl] = None
    facebook: Optional[HttpUrl] = None
    tiktok: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    youtube: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    pinterest: Optional[HttpUrl] = None

class Contact(BaseModel):
    emails: List[EmailStr] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)

class ImportantLinks(BaseModel):
    tracking: Optional[HttpUrl] = None
    contact_us: Optional[HttpUrl] = None
    blogs: Optional[HttpUrl] = None
    sitemap: Optional[HttpUrl] = None

class BrandContext(BaseModel):
    brand: Optional[str] = None
    domain: Optional[str] = None
    product_catalog: List[Product] = Field(default_factory=list)
    hero_products: List[Product] = Field(default_factory=list)
    policies: Dict[str, Policy] = Field(default_factory=dict)
    faqs: List[FAQ] = Field(default_factory=list)
    socials: SocialHandle = SocialHandle()
    contacts: Contact = Contact()
    about: Dict[str, Optional[str]] = Field(default_factory=dict)
    important_links: ImportantLinks = ImportantLinks()
    timestamp: Optional[str] = None
