import httpx
import asyncio
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
from app.models.schemas import BrandContext, Product, Policy, FAQ, SocialHandle, Contact, ImportantLinks
from app.services.detectors import (
    is_shopify, extract_socials, extract_emails_and_phones,
    guess_about_url, guess_contact_url, guess_blog_url, guess_tracking_url,
    extract_faqs, extract_hero_products_from_home
)
from datetime import datetime
import json
import logging
import re

logger = logging.getLogger(__name__)

class ShopifyFetcher:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def fetch_url(self, url: str) -> Optional[tuple]:
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text, dict(response.headers)
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None, {}
    
    async def fetch_brand_context(self, website_url: str) -> Optional[BrandContext]:
        try:
            if not website_url.startswith(('http://', 'https://')):
                website_url = f"https://{website_url}"
            
            home_content, headers = await self.fetch_url(website_url)
            if not home_content:
                return None
            
            if not is_shopify(home_content, headers):
                logger.warning(f"{website_url} doesn't appear to be a Shopify store")
            
            soup = BeautifulSoup(home_content, 'html.parser')
            
            brand_context = BrandContext()
            brand_context.domain = urlparse(website_url).netloc
            brand_context.timestamp = datetime.now().isoformat()
            
            brand_context.brand = self.extract_brand_name(soup, website_url)
            
            tasks = [
                self.fetch_product_catalog(website_url),
                self.fetch_hero_products(soup, website_url),
                self.fetch_policies(website_url),
                self.fetch_faqs(soup, website_url),
                self.fetch_socials_and_contacts(soup, website_url),
                self.fetch_about_info(soup, website_url),
                self.fetch_important_links(soup, website_url)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            brand_context.product_catalog = results[0] if not isinstance(results[0], Exception) else []
            brand_context.hero_products = results[1] if not isinstance(results[1], Exception) else []
            brand_context.policies = results[2] if not isinstance(results[2], Exception) else {}
            brand_context.faqs = results[3] if not isinstance(results[3], Exception) else []
            
            if not isinstance(results[4], Exception):
                brand_context.socials, brand_context.contacts = results[4]
            
            brand_context.about = results[5] if not isinstance(results[5], Exception) else {}
            brand_context.important_links = results[6] if not isinstance(results[6], Exception) else ImportantLinks()
            
            return brand_context
            
        except Exception as e:
            logger.error(f"Error fetching brand context: {str(e)}")
            return None
    
    def extract_brand_name(self, soup: BeautifulSoup, website_url: str) -> str:
        """Extract brand name from various sources"""
        title = soup.find('title')
        if title:
            brand_name = title.get_text().strip()
            for suffix in [' | Shopify', ' - Shopify', ' Store', ' Shop']:
                if brand_name.endswith(suffix):
                    brand_name = brand_name[:-len(suffix)].strip()
            if brand_name:
                return brand_name
        
        logo = soup.find('img', {'class': re.compile(r'logo', re.I)})
        if logo and logo.get('alt'):
            return logo['alt'].strip()
        
        return urlparse(website_url).netloc.replace('www.', '')
    
    async def fetch_product_catalog(self, website_url: str) -> List[Product]:
        products = []
        try:
            products_url = urljoin(website_url, '/products.json')
            content, _ = await self.fetch_url(products_url)
            
            if content:
                data = json.loads(content)
                for product_data in data.get('products', []):
                    product = Product(
                        id=str(product_data.get('id', '')),
                        title=product_data.get('title', ''),
                        price=self.format_price(product_data.get('variants', [{}])[0].get('price')),
                        url=urljoin(website_url, f"/products/{product_data.get('handle', '')}"),
                        image=product_data.get('images', [{}])[0].get('src') if product_data.get('images') else None,
                        available=any(v.get('available', False) for v in product_data.get('variants', []))
                    )
                    products.append(product)
        
        except Exception as e:
            logger.error(f"Error fetching product catalog: {str(e)}")
        
        return products
    
    async def fetch_hero_products(self, soup: BeautifulSoup, website_url: str) -> List[Product]:
        try:
            hero_data = extract_hero_products_from_home(soup, website_url)
            hero_products = []
            
            for item in hero_data[:10]:  
                product = Product(
                    title=item.get('title'),
                    url=item.get('url')
                )
                hero_products.append(product)
            
            return hero_products
        except Exception as e:
            logger.error(f"Error fetching hero products: {str(e)}")
            return []
    
    async def fetch_policies(self, website_url: str) -> Dict[str, Policy]:
        policies = {}
        policy_types = {
            'privacy': ['/pages/privacy-policy', '/privacy', '/privacy-policy'],
            'return': ['/pages/return-policy', '/pages/returns', '/return-policy', '/returns'],
            'refund': ['/pages/refund-policy', '/pages/refunds', '/refund-policy', '/refunds'],
            'terms': ['/pages/terms-of-service', '/pages/terms', '/terms', '/terms-of-service'],
            'shipping': ['/pages/shipping-policy', '/pages/shipping', '/shipping-policy', '/shipping']
        }
        
        for policy_name, paths in policy_types.items():
            for path in paths:
                policy_url = urljoin(website_url, path)
                content, _ = await self.fetch_url(policy_url)
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                        tag.decompose()
                    
                    text = soup.get_text(separator=' ', strip=True)
                    if len(text) > 100:  
                        policies[policy_name] = Policy(url=policy_url, text=text[:1000])
                        break
        
        return policies
    
    async def fetch_faqs(self, soup: BeautifulSoup, website_url: str) -> List[FAQ]:
        faqs = []
        
        homepage_faqs = extract_faqs(soup, website_url)
        faqs.extend([FAQ(**faq) for faq in homepage_faqs])
        
        faq_paths = ['/pages/faq', '/pages/faqs', '/faq', '/faqs', '/pages/help']
        for path in faq_paths:
            faq_url = urljoin(website_url, path)
            content, _ = await self.fetch_url(faq_url)
            
            if content:
                faq_soup = BeautifulSoup(content, 'html.parser')
                page_faqs = extract_faqs(faq_soup, faq_url)
                faqs.extend([FAQ(**faq) for faq in page_faqs])
                if page_faqs: 
                    break
        
        return faqs[:20]  # Limit to 20 FAQs
    
    async def fetch_socials_and_contacts(self, soup: BeautifulSoup, website_url: str) -> tuple:
        socials_data = extract_socials(soup, website_url)
        socials = SocialHandle(**socials_data)
        
        text_content = soup.get_text()
        emails, phones = extract_emails_and_phones(text_content)
        
        contact_url = guess_contact_url(soup, website_url)
        if contact_url:
            contact_content, _ = await self.fetch_url(contact_url)
            if contact_content:
                contact_soup = BeautifulSoup(contact_content, 'html.parser')
                contact_text = contact_soup.get_text()
                page_emails, page_phones = extract_emails_and_phones(contact_text)
                emails.extend(page_emails)
                phones.extend(page_phones)
        
        emails = list(set(emails))
        phones = list(set(phones))
        
        contacts = Contact(emails=emails, phones=phones)
        
        return socials, contacts
    
    async def fetch_about_info(self, soup: BeautifulSoup, website_url: str) -> Dict[str, str]:
        about_info = {}
        
        about_url = guess_about_url(soup, website_url)
        
        if about_url:
            content, _ = await self.fetch_url(about_url)
            if content:
                about_soup = BeautifulSoup(content, 'html.parser')
                for tag in about_soup(['script', 'style', 'nav', 'header', 'footer']):
                    tag.decompose()
                
                text = about_soup.get_text(separator=' ', strip=True)
                about_info['text'] = text[:2000]  
                about_info['url'] = about_url
        
        if not about_info.get('text'):
            about_sections = soup.find_all(['section', 'div'], class_=lambda c: c and 'about' in c.lower())
            if about_sections:
                text = about_sections[0].get_text(separator=' ', strip=True)
                if len(text) > 50:
                    about_info['text'] = text[:1000]
        
        return about_info
    
    async def fetch_important_links(self, soup: BeautifulSoup, website_url: str) -> ImportantLinks:
        links = ImportantLinks()
        
        links.tracking = guess_tracking_url(soup, website_url)
        links.contact_us = guess_contact_url(soup, website_url)
        links.blogs = guess_blog_url(soup, website_url)
        
        sitemap_url = urljoin(website_url, '/sitemap.xml')
        content, _ = await self.fetch_url(sitemap_url)
        if content and '<urlset' in content:
            links.sitemap = sitemap_url
        
        return links
    
    def format_price(self, price) -> str:
        if price is None:
            return None
        
        try:
            price_float = float(price)
            return f"${price_float:.2f}"
        except (ValueError, TypeError):
            return str(price) if price else None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()