from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.services.fetcher import ShopifyFetcher
from app.models.schemas import BrandContext
from app.models.db import SessionLocal
from app.models.orm import Brand, ProductORM
from sqlalchemy import select
import logging

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/fetch-insights", response_model=BrandContext)
async def fetch_shopify_insights(
    website_url: str = Query(..., description="Shopify store URL"),
    save_to_db: bool = Query(False, description="Save results to database"),
    db: AsyncSession = Depends(get_db)
):

    try:
        if not website_url.startswith(('http://', 'https://')):
            website_url = f"https://{website_url}"
        
        fetcher = ShopifyFetcher()
        
        brand_context = await fetcher.fetch_brand_context(website_url)
        
        if not brand_context:
            raise HTTPException(status_code=404, detail="Website not found or not accessible")
        
        if save_to_db:
            await save_brand_to_db(db, brand_context, website_url)
        
        return brand_context
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/brands", response_model=list)
async def get_all_brands(db: AsyncSession = Depends(get_db)):

    try:
        result = await db.execute(select(Brand))
        brands = result.scalars().all()
        return [{"id": b.id, "name": b.name, "website": b.website, "about": b.about} for b in brands]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/brands/{brand_id}", response_model=dict)
async def get_brand_details(brand_id: int, db: AsyncSession = Depends(get_db)):

    try:
        brand_result = await db.execute(select(Brand).where(Brand.id == brand_id))
        brand = brand_result.scalar_one_or_none()
        
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        products_result = await db.execute(select(ProductORM).where(ProductORM.brand_id == brand_id))
        products = products_result.scalars().all()
        
        return {
            "brand": {
                "id": brand.id,
                "name": brand.name,
                "website": brand.website,
                "about": brand.about
            },
            "products": [
                {
                    "id": p.id,
                    "title": p.title,
                    "url": p.url,
                    "price": p.price,
                    "sku": p.sku,
                    "available": p.available,
                    "image": p.image
                } for p in products
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/brands/{brand_id}")
async def delete_brand(brand_id: int, db: AsyncSession = Depends(get_db)):

    try:
        brand_result = await db.execute(select(Brand).where(Brand.id == brand_id))
        brand = brand_result.scalar_one_or_none()
        
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        await db.delete(brand)
        await db.commit()
        
        return {"message": "Brand deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def save_brand_to_db(db: AsyncSession, brand_context: BrandContext, website_url: str):

    try:
        result = await db.execute(select(Brand).where(Brand.website == website_url))
        existing_brand = result.scalar_one_or_none()
        
        if existing_brand:
            existing_brand.name = brand_context.brand
            existing_brand.about = brand_context.about.get('text', '')
            brand = existing_brand
        else:
            brand = Brand(
                website=website_url,
                name=brand_context.brand,
                about=brand_context.about.get('text', '')
            )
            db.add(brand)
            
        await db.flush()  
        
        # Save products
        for product in brand_context.product_catalog:
            product_orm = ProductORM(
                brand_id=brand.id,
                handle=product.id,
                title=product.title,
                url=str(product.url) if product.url else "",
                price=product.price,
                sku="",
                available=product.available,
                image=str(product.image) if product.image else ""
            )
            db.add(product_orm)
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise e