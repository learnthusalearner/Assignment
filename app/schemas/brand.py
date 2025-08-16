from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict



class BrandRequest(BaseModel):
    website_url: HttpUrl   # input from user


class Product(BaseModel):
    name: str
    url: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None


class BrandContext(BaseModel):
    brand: str
    domain: str
    product_catalog: List[Product] = []
    hero_products: List[Product] = []
    policies: Dict[str, str] = {}
    faqs: List[str] = []
    socials: Dict[str, str] = {}
