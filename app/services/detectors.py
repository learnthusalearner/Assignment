import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

SOCIAL_HOSTS = {
    "instagram.com": "instagram",
    "facebook.com": "facebook", 
    "tiktok.com": "tiktok",
    "twitter.com": "twitter",
    "x.com": "twitter",
    "youtube.com": "youtube",
    "linkedin.com": "linkedin",
    "pinterest.com": "pinterest",
}

EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE_RE = re.compile(r'(?:\+?\d[\d\s\-\(\)\.]{7,}\d)')

def is_shopify(html_text: str, headers: dict) -> bool:
    shopify_headers = [
        'x-shopify-stage', 'x-shopify-shop-api-call-limit', 
        'server-timing', 'x-shopify-request-id'
    ]
    
    if any(h.lower() in [k.lower() for k in headers.keys()] for h in shopify_headers):
        return True
    
    shopify_indicators = [
        'cdn.shopify.com',
        'Shopify.theme',
        'shopify_section',
        'shopify-section',
        'window.Shopify',
        'Shopify.money_format'
    ]
    
    return any(indicator in html_text for indicator in shopify_indicators)

def extract_socials(soup: BeautifulSoup, base: str) -> Dict[str, Optional[str]]:
    found = {platform: None for platform in SOCIAL_HOSTS.values()}
    
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        
        for host, platform in SOCIAL_HOSTS.items():
            if host in href:
                full_url = urljoin(base, a["href"])
                if f"//{host}" in full_url or f".{host}" in full_url:
                    found[platform] = full_url
                    break
    
    social_images = soup.find_all("img", src=True)
    for img in social_images:
        src = img["src"].lower()
        alt = (img.get("alt") or "").lower()
        
        for host, platform in SOCIAL_HOSTS.items():
            if platform in src or platform in alt:
                parent_link = img.find_parent("a")
                if parent_link and parent_link.get("href"):
                    href = parent_link["href"].lower()
                    if host in href:
                        found[platform] = urljoin(base, parent_link["href"])
    
    return found

def extract_emails_and_phones(text: str) -> Tuple[List[str], List[str]]:
    emails = list(set(EMAIL_RE.findall(text)))
    
    phones = []
    phone_matches = PHONE_RE.findall(text)
    for phone in phone_matches:
        clean_phone = re.sub(r'[^\d\+\-\(\)\s\.]', '', phone)
        digits_only = re.sub(r'[^\d]', '', clean_phone)
        if 7 <= len(digits_only) <= 15:
            phones.append(clean_phone.strip())
    
    phones = list(set(phones))
    
    emails = [e for e in emails if not any(fp in e.lower() for fp in ['example.com', 'test.com', 'domain.com'])]
    
    return emails, phones

def _find_link_by_terms(soup: BeautifulSoup, terms: List[str], base: str) -> Optional[str]:
    for a in soup.find_all("a", href=True):
        link_text = (a.get_text() or "").strip().lower()
        href = a["href"].lower()
        
        if any(term in link_text or term in href for term in terms):
            return urljoin(base, a["href"])
    
    return None

def guess_about_url(soup: BeautifulSoup, base: str) -> Optional[str]:
    about_terms = ["about", "our story", "who we are", "about us", "company", "mission"]
    return _find_link_by_terms(soup, about_terms, base)

def guess_contact_url(soup: BeautifulSoup, base: str) -> Optional[str]:
    contact_terms = ["contact", "support", "contact us", "get in touch", "reach us"]
    return _find_link_by_terms(soup, contact_terms, base)

def guess_blog_url(soup: BeautifulSoup, base: str) -> Optional[str]:
    for a in soup.find_all("a", href=True):
        if "/blogs" in a["href"]:
            return urljoin(base, a["href"])
    
    blog_terms = ["blog", "news", "articles", "stories", "journal"]
    return _find_link_by_terms(soup, blog_terms, base)

def guess_tracking_url(soup: BeautifulSoup, base: str) -> Optional[str]:
    tracking_terms = ["track", "tracking", "order status", "track order", "my orders"]
    return _find_link_by_terms(soup, tracking_terms, base)

def extract_faqs(soup: BeautifulSoup, base: str) -> List[Dict[str, str]]:
    faqs = []
    
    for details in soup.find_all("details"):
        summary = details.find("summary")
        if summary:
            question = summary.get_text(strip=True)
            content = details.get_text(separator=" ", strip=True)
            if len(content) > len(question):
                answer = content.replace(question, "", 1).strip()
                if answer and len(answer) > 10:  
                    faqs.append({
                        "question": question,
                        "answer": answer[:500], 
                        "url": base
                    })
    
    faq_selectors = [
        {'class': re.compile(r'faq', re.I)},
        {'class': re.compile(r'accordion', re.I)},
        {'class': re.compile(r'question', re.I)},
        {'id': re.compile(r'faq', re.I)}
    ]
    
    for selector in faq_selectors:
        wrappers = soup.find_all(["div", "section", "article"], selector)
        for wrapper in wrappers:
            questions = wrapper.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b"])
            for q_elem in questions:
                question = q_elem.get_text(strip=True)
                if not question or len(question) < 5:
                    continue
                
                answer_elem = q_elem.find_next_sibling(["p", "div", "span"])
                if not answer_elem:
                    parent = q_elem.find_parent()
                    if parent:
                        answer_elem = parent.find_next_sibling(["p", "div"])
                
                if answer_elem:
                    answer = answer_elem.get_text(separator=" ", strip=True)
                    if answer and len(answer) > 10 and len(answer) < 1000:
                        faqs.append({
                            "question": question,
                            "answer": answer,
                            "url": base
                        })
    
    faq_buttons = soup.find_all(["button", "div"], class_=re.compile(r'faq|accordion|toggle', re.I))
    for button in faq_buttons:
        question = button.get_text(strip=True)
        if not question or len(question) < 5:
            continue
        
        target_id = button.get('aria-controls') or button.get('data-target')
        if target_id:
            target = soup.find(id=target_id.replace('#', ''))
            if target:
                answer = target.get_text(separator=" ", strip=True)
                if answer and len(answer) > 10:
                    faqs.append({
                        "question": question,
                        "answer": answer[:500],
                        "url": base
                    })
    
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    for script in json_ld_scripts:
        try:
            import json
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get('@type') == 'FAQPage':
                main_entity = data.get('mainEntity', [])
                for item in main_entity:
                    if item.get('@type') == 'Question':
                        question = item.get('name', '')
                        accepted_answer = item.get('acceptedAnswer', {})
                        answer = accepted_answer.get('text', '')
                        if question and answer:
                            faqs.append({
                                "question": question,
                                "answer": answer[:500],
                                "url": base
                            })
        except (json.JSONDecodeError, KeyError, TypeError):
            continue
    
    for dl in soup.find_all('dl'):
        dts = dl.find_all('dt')
        for dt in dts:
            question = dt.get_text(strip=True)
            dd = dt.find_next_sibling('dd')
            if dd and question:
                answer = dd.get_text(separator=" ", strip=True)
                if answer and len(answer) > 10:
                    faqs.append({
                        "question": question,
                        "answer": answer[:500],
                        "url": base
                    })
    
    text_content = soup.get_text(separator='\n')
    qa_patterns = [
        r'Q[:\.]?\s*(.*?)\n.*?A[:\.]?\s*(.*?)(?:\n|$)',
        r'Question[:\.]?\s*(.*?)\n.*?Answer[:\.]?\s*(.*?)(?:\n|$)',
        r'\b\d+\.\s*(.*?\?.*?)\n(.*?)(?:\n\d+\.|$)'
    ]
    
    for pattern in qa_patterns:
        matches = re.findall(pattern, text_content, re.MULTILINE | re.DOTALL)
        for match in matches:
            if len(match) == 2:
                question = match[0].strip()
                answer = match[1].strip()
                if question and answer and len(question) > 5 and len(answer) > 10:
                    faqs.append({
                        "question": question[:200],
                        "answer": answer[:500],
                        "url": base
                    })
    
    unique_faqs = []
    seen_questions = set()
    
    for faq in faqs:
        question_key = faq['question'].lower().strip()[:50]  
        if question_key not in seen_questions and len(question_key) > 5:
            seen_questions.add(question_key)
            unique_faqs.append(faq)
    
    return unique_faqs[:15]  

def extract_hero_products_from_home(soup: BeautifulSoup, base: str) -> List[Dict[str, str]]:
    """Extract hero/featured products from homepage"""
    hero_products = []
    seen_urls = set()
    
    main_selectors = [
        'main', '[role="main"]', '.main-content', '#main',
        '.hero', '.featured', '.products', '.collection',
        '.homepage-products', '.featured-products'
    ]
    
    for selector in main_selectors:
        container = soup.select_one(selector)
        if container:
            product_links = container.find_all("a", href=True)
            for link in product_links:
                href = link["href"]
                if "/products/" in href:
                    full_url = urljoin(base, href)
                    if full_url not in seen_urls:
                        seen_urls.add(full_url)
                        
                        title = link.get_text(strip=True)
                        
                        if not title:
                            img = link.find("img")
                            if img and img.get("alt"):
                                title = img["alt"].strip()
                        
                        if not title:
                            title = link.get("aria-label", "").strip()
                        
                        if not title:
                            title = link.get("data-product-title", "").strip()
                        
                        hero_products.append({
                            "url": full_url,
                            "title": title or "Product"
                        })
                        
                        if len(hero_products) >= 20: 
                            break
            
            if hero_products: 
                break
    
    if not hero_products:
        all_product_links = soup.find_all("a", href=True)
        for link in all_product_links:
            href = link["href"]
            if "/products/" in href:
                full_url = urljoin(base, href)
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    title = link.get_text(strip=True) or "Product"
                    hero_products.append({
                        "url": full_url,
                        "title": title
                    })
                    
                    if len(hero_products) >= 10:
                        break
    
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    for script in json_ld_scripts:
        try:
            import json
            data = json.loads(script.string)
            
            products_data = []
            if isinstance(data, list):
                products_data = data
            elif isinstance(data, dict):
                if data.get('@type') == 'Product':
                    products_data = [data]
                elif 'mainEntity' in data:
                    main_entity = data['mainEntity']
                    if isinstance(main_entity, list):
                        products_data = [item for item in main_entity if item.get('@type') == 'Product']
            
            for product_data in products_data:
                if product_data.get('@type') == 'Product':
                    name = product_data.get('name', '')
                    url = product_data.get('url', '')
                    
                    if name and url:
                        full_url = urljoin(base, url)
                        if full_url not in seen_urls:
                            seen_urls.add(full_url)
                            hero_products.append({
                                "url": full_url,
                                "title": name
                            })
                        
                        if len(hero_products) >= 20:
                            break
                            
        except (json.JSONDecodeError, KeyError, TypeError):
            continue
    
    return hero_products

def extract_product_info_from_page(soup: BeautifulSoup, url: str) -> Dict[str, str]:
    """Extract product information from a product page"""
    product_info = {"url": url}
    
    title_selectors = [
        'h1.product-title', 'h1.product-name', '.product-title', 
        '.product-name', 'h1', '[data-product-title]'
    ]
    
    for selector in title_selectors:
        title_elem = soup.select_one(selector)
        if title_elem:
            product_info["title"] = title_elem.get_text(strip=True)
            break
    
    price_selectors = [
        '.price', '.product-price', '[data-price]', '.money',
        '.price-current', '.sale-price', '.regular-price'
    ]
    
    for selector in price_selectors:
        price_elem = soup.select_one(selector)
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r'[\$£€¥]?(\d+(?:\.\d{2})?)', price_text)
            if price_match:
                product_info["price"] = price_match.group(0)
                break
    
    image_selectors = [
        '.product-image img', '.product-photo img', '[data-product-image]',
        '.main-image img', '.hero-image img'
    ]
    
    for selector in image_selectors:
        img_elem = soup.select_one(selector)
        if img_elem and img_elem.get('src'):
            product_info["image"] = urljoin(url, img_elem['src'])
            break
    
    availability_indicators = [
        '.in-stock', '.available', '.out-of-stock', '.sold-out',
        '[data-availability]', '.inventory-status'
    ]
    
    for selector in availability_indicators:
        availability_elem = soup.select_one(selector)
        if availability_elem:
            text = availability_elem.get_text().lower()
            if 'out of stock' in text or 'sold out' in text:
                product_info["available"] = False
            elif 'in stock' in text or 'available' in text:
                product_info["available"] = True
            break
    
    if "available" not in product_info:
        add_to_cart = soup.select_one('[data-add-to-cart], .add-to-cart, .btn-add-to-cart')
        if add_to_cart:
            product_info["available"] = not add_to_cart.get('disabled')
        else:
            product_info["available"] = True
    
    return product_info

def extract_breadcrumbs(soup: BeautifulSoup, base: str) -> List[Dict[str, str]]:
    """Extract breadcrumb navigation"""
    breadcrumbs = []
    
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    for script in json_ld_scripts:
        try:
            import json
            data = json.loads(script.string)
            if data.get('@type') == 'BreadcrumbList':
                for item in data.get('itemListElement', []):
                    breadcrumbs.append({
                        'name': item.get('name', ''),
                        'url': urljoin(base, item.get('item', ''))
                    })
                return breadcrumbs
        except (json.JSONDecodeError, KeyError, TypeError):
            continue
    
    breadcrumb_selectors = [
        '.breadcrumb', '.breadcrumbs', '[data-breadcrumb]',
        '.navigation-breadcrumbs', '.page-breadcrumb'
    ]
    
    for selector in breadcrumb_selectors:
        breadcrumb_elem = soup.select_one(selector)
        if breadcrumb_elem:
            links = breadcrumb_elem.find_all('a', href=True)
            for link in links:
                breadcrumbs.append({
                    'name': link.get_text(strip=True),
                    'url': urljoin(base, link['href'])
                })
            break
    
    return breadcrumbs

def extract_reviews(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Extract product reviews"""
    reviews = []
    
    review_selectors = [
        '.review', '.reviews', '.testimonial', '.testimonials',
        '[data-review]', '.customer-review'
    ]
    
    for selector in review_selectors:
        review_elems = soup.select(selector)
        for elem in review_elems:
            review_text = elem.get_text(separator=' ', strip=True)
            if len(review_text) > 20:  # Ensure meaningful review
                reviews.append({
                    'text': review_text[:500],  # Limit length
                    'rating': extract_rating_from_element(elem)
                })
            
            if len(reviews) >= 10:  
                break
    
    return reviews

def extract_rating_from_element(elem) -> Optional[str]:
    stars = elem.find_all(class_=re.compile(r'star', re.I))
    if stars:
        filled_stars = elem.find_all(class_=re.compile(r'filled|full', re.I))
        return f"{len(filled_stars)}/5"
    
    rating_text = elem.get_text()
    rating_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:out of|/|stars?)', rating_text, re.I)
    if rating_match:
        return rating_match.group(1)
    
    return None

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = ' '.join(text.split())
    
    text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def is_valid_url(url: str, base_domain: str) -> bool:
    try:
        parsed = urlparse(url)
        base_parsed = urlparse(base_domain)
        
        return parsed.netloc == base_parsed.netloc or parsed.netloc.endswith(f'.{base_parsed.netloc}')
    except:
        return False

def extract_currency_from_text(text: str) -> Optional[str]:
    currency_symbols = ['$', '€', '£', '¥', '₹', '¢']
    currency_codes = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD']
    
    for symbol in currency_symbols:
        if symbol in text:
            return symbol
    
    for code in currency_codes:
        if code in text.upper():
            return code
    
    return None

def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
    meta_data = {}
    
    # Common meta tags
    meta_tags = {
        'description': ['name="description"', 'property="og:description"'],
        'title': ['property="og:title"', 'name="twitter:title"'],
        'image': ['property="og:image"', 'name="twitter:image"'],
        'url': ['property="og:url"', 'name="twitter:url"'],
        'type': ['property="og:type"'],
        'site_name': ['property="og:site_name"']
    }
    
    for key, selectors in meta_tags.items():
        for selector in selectors:
            meta_elem = soup.find('meta', attrs=selector.split('=')[0].split('name')[1] if 'name' in selector else selector.split('=')[0].split('property')[1])
            if meta_elem:
                meta_data[key] = meta_elem.get('content', '')
                break
    
    return meta_data

def detect_ecommerce_platform(soup: BeautifulSoup, headers: dict, html_text: str) -> str:
    if is_shopify(html_text, headers):
        return 'Shopify'
    
    platform_indicators = {
        'WooCommerce': ['wp-content', 'woocommerce'],
        'Magento': ['Magento', 'mage/cookies'],
        'BigCommerce': ['bigcommerce.com', 'bc-sf-filter'],
        'Squarespace': ['squarespace.com', 'squarespace'],
        'Wix': ['wix.com', '_wix'],
        'PrestaShop': ['prestashop', 'ps_'],
        'OpenCart': ['opencart', 'journal_']
    }
    
    for platform, indicators in platform_indicators.items():
        if any(indicator.lower() in html_text.lower() for indicator in indicators):
            return platform
    
    return 'Unknown'