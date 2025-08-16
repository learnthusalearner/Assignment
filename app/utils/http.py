import httpx
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)

class HTTPClient:
    """Enhanced HTTP client with retry logic and better error handling"""
    
    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers=self.headers,
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=100)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def get(self, url: str, **kwargs) -> Optional[httpx.Response]:
        """Make GET request with retry logic"""
        if not self.client:
            raise RuntimeError("HTTP client not initialized. Use async context manager.")
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.get(url, **kwargs)
                
                # Consider 4xx as non-retryable errors
                if 400 <= response.status_code < 500:
                    logger.warning(f"Client error {response.status_code} for {url}")
                    return response
                
                # Retry on 5xx errors
                if response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code} for {url}, attempt {attempt + 1}/{self.max_retries}")
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                
                response.raise_for_status()
                return response
                
            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Timeout for {url}, attempt {attempt + 1}/{self.max_retries}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            except httpx.NetworkError as e:
                last_error = e
                logger.warning(f"Network error for {url}, attempt {attempt + 1}/{self.max_retries}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error for {url}: {str(e)}")
                break
        
        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts: {str(last_error)}")
        return None
    
    async def get_text(self, url: str, **kwargs) -> Optional[str]:
        """Get text content from URL"""
        response = await self.get(url, **kwargs)
        if response and response.status_code == 200:
            return response.text
        return None
    
    async def get_json(self, url: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """Get JSON content from URL"""
        response = await self.get(url, **kwargs)
        if response and response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                logger.error(f"Failed to parse JSON from {url}: {str(e)}")
        return None

def normalize_url(url: str) -> str:
    if not url:
        return url
    
    url = url.strip()
    
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    if url.endswith('/') and len(url) > 8:  
        url = url.rstrip('/')
    
    return url

def is_same_domain(url1: str, url2: str) -> bool:
    try:
        domain1 = urlparse(url1).netloc.lower()
        domain2 = urlparse(url2).netloc.lower()
        
        # Remove www prefix for comparison
        domain1 = domain1.replace('www.', '')
        domain2 = domain2.replace('www.', '')
        
        return domain1 == domain2
    except:
        return False

def get_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except:
        return ""

def build_absolute_url(base_url: str, relative_url: str) -> str:
    """Build absolute URL from base and relative URLs"""
    try:
        return urljoin(base_url, relative_url)
    except:
        return relative_url

class RateLimiter:
    
    def __init__(self, max_requests: int = 10, time_window: float = 1.0):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        async with self._lock:
            now = asyncio.get_event_loop().time()
            
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            if len(self.requests) >= self.max_requests:
                sleep_time = self.time_window - (now - self.requests[0]) + 0.1
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    self.requests.pop(0)
            
            self.requests.append(now)

async def batch_fetch_urls(urls: list, max_concurrent: int = 5, timeout: float = 30.0) -> dict:
    """Fetch multiple URLs concurrently with rate limiting"""
    semaphore = asyncio.Semaphore(max_concurrent)
    rate_limiter = RateLimiter(max_requests=10, time_window=1.0)
    results = {}
    
    async def fetch_single(url: str):
        async with semaphore:
            await rate_limiter.acquire()
            async with HTTPClient(timeout=timeout) as client:
                response = await client.get(url)
                if response and response.status_code == 200:
                    results[url] = response.text
                else:
                    results[url] = None
    
    tasks = [fetch_single(url) for url in urls if url]
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

def clean_url_params(url: str, keep_params: list = None) -> str:
    if not url:
        return url
    
    try:
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed = urlparse(url)
        if not parsed.query:
            return url
        
        if keep_params:
            params = parse_qs(parsed.query)
            cleaned_params = {k: v for k, v in params.items() if k in keep_params}
            query = urlencode(cleaned_params, doseq=True)
        else:
            query = ""
        
        return urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, query, parsed.fragment
        ))
    except:
        return url

def extract_domain_info(url: str) -> dict:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        clean_domain = domain.replace('www.', '')
        
        parts = clean_domain.split('.')
        tld = parts[-1] if len(parts) > 1 else ""
        
        subdomain = ""
        if len(parts) > 2:
            subdomain = '.'.join(parts[:-2])
        
        return {
            "full_domain": domain,
            "clean_domain": clean_domain,
            "subdomain": subdomain,
            "tld": tld,
            "scheme": parsed.scheme,
            "port": parsed.port
        }
    except:
        return {}