# Shopify Insights Fetcher

A robust FastAPI application that extracts comprehensive insights from Shopify stores without using the official Shopify API. The application scrapes and analyzes Shopify websites to gather brand information, product catalogs, policies, FAQs, social handles, and more.

## Features

### Mandatory Features ✅
- **Product Catalog**: Complete list of products from the store
- **Hero Products**: Featured products from the homepage
- **Policies**: Privacy, Return, Refund, Terms of Service, and Shipping policies
- **FAQs**: Frequently Asked Questions with answers
- **Social Handles**: Instagram, Facebook, TikTok, Twitter, YouTube, LinkedIn, Pinterest
- **Contact Information**: Email addresses and phone numbers
- **Brand Context**: About information and brand description
- **Important Links**: Order tracking, Contact Us, Blogs, Sitemap

### Bonus Features ✅
- **Database Persistence**: Store all data in SQLite/MySQL database
- **RESTful API**: Clean API design with proper error handling
- **Async Processing**: High-performance asynchronous operations
- **Rate Limiting**: Respectful scraping with built-in rate limits

## Project Structure

```
gen-ai-ass/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── fetcher.py       # Main scraping logic
│   │   └── detectors.py     # Content detection utilities
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db.py           # Database configuration
│   │   ├── orm.py          # SQLAlchemy models
│   │   └── schemas.py      # Pydantic models
│   └── utils/
│       ├── __init__.py
│       └── http.py         # HTTP utilities
├── init_db.py              # Database initialization
├── requirements.txt        # Python dependencies
└── README.md
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gen-ai-ass
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python init_db.py
   ```

## Usage

### Starting the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### 1. Fetch Store Insights
```http
POST /api/v1/fetch-insights?website_url=https://memy.co.in&save_to_db=true
```

**Parameters:**
- `website_url` (required): Shopify store URL
- `save_to_db` (optional): Save results to database (default: false)

**Response:**
```json
{
  "brand": "Memy",
  "domain": "memy.co.in",
  "product_catalog": [...],
  "hero_products": [...],
  "policies": {...},
  "faqs": [...],
  "socials": {...},
  "contacts": {...},
  "about": {...},
  "important_links": {...},
  "timestamp": "2024-01-01T12:00:00"
}
```

#### 2. Get All Brands
```http
GET /api/v1/brands
```

#### 3. Get Brand Details
```http
GET /api/v1/brands/{brand_id}
```

#### 4. Delete Brand
```http
DELETE /api/v1/brands/{brand_id}
```

### Example Usage with cURL

```bash
# Fetch insights from a Shopify store
curl -X POST "http://localhost:8000/api/v1/fetch-insights?website_url=https://memy.co.in&save_to_db=true"

# Get all stored brands
curl -X GET "http://localhost:8000/api/v1/brands"
```

### Example Usage with Python

```python
import httpx
import asyncio

async def fetch_insights():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/fetch-insights",
            params={
                "website_url": "https://memy.co.in",
                "save_to_db": True
            }
        )
        return response.json()

# Run the function
insights = asyncio.run(fetch_insights())
print(insights)
```

## Supported Shopify Stores

The application works with any Shopify store. Here are some examples you can test:

- https://memy.co.in
- https://hairoriginals.com
- https://colourpop.com
- https://gymshark.com
- https://allbirds.com

## Technical Details

### Detection Methods

1. **Shopify Detection**: Identifies Shopify stores using headers and HTML content
2. **Product Catalog**: Uses `/products.json` endpoint for complete product data
3. **Content Extraction**: BeautifulSoup for HTML parsing and content extraction
4. **Social Media**: Pattern matching for social media URLs
5. **Contact Info**: Regex patterns for emails and phone numbers

### Error Handling

- **404**: Website not found or inaccessible
- **500**: Internal server errors with detailed logging
- **Rate Limiting**: Respectful scraping with delays
- **Timeouts**: Configurable request timeouts

### Database Schema

```sql
-- Brands table
CREATE TABLE brands (
    id INTEGER PRIMARY KEY,
    website VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    about TEXT
);

-- Products table  
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    handle VARCHAR(255),
    title VARCHAR(255),
    url VARCHAR(500),
    price VARCHAR(50),
    sku VARCHAR(100),
    available BOOLEAN,
    image VARCHAR(500)
);
```

## Performance Optimization

- **Async Operations**: Non-blocking I/O for high concurrency
- **Connection Pooling**: Reuse HTTP connections
- **Rate Limiting**: Prevent overwhelming target servers
- **Concurrent Fetching**: Parallel requests for different data types
- **Caching**: Database persistence for repeated queries

## Configuration

### Environment Variables

```bash
# Database URL (default: SQLite)
DATABASE_URL=sqlite+aiosqlite:///./shopify_insights.db

# For MySQL
DATABASE_URL=mysql+aiomysql://user:password@localhost/shopify_insights

# Logging level
LOG_LEVEL=INFO
```

### Customization

You can customize the scraping behavior by modifying:

- `app/services/detectors.py`: Content detection patterns
- `app/services/fetcher.py`: Scraping logic and data extraction
- `app/models/schemas.py`: Data models and validation

## Testing

### Manual Testing with Postman

1. Import the API endpoints into Postman
2. Test the `/fetch-insights` endpoint with different Shopify stores
3. Verify the data structure and completeness

### Testing with Different Stores

```bash
# Test with different store types
curl -X POST "http://localhost:8000/api/v1/fetch-insights?website_url=https://memy.co.in"
curl -X POST "http://localhost:8000/api/v1/fetch-insights?website_url=https://colourpop.com"
curl -X POST "http://localhost:8000/api/v1/fetch-insights?website_url=https://gymshark.com"
```

## Limitations

- Respects robots.txt and implements rate limiting
- Some dynamic content may require JavaScript execution
- Store-specific customizations might affect data extraction
- Rate limits prevent aggressive scraping

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes with tests
4. Submit a pull request

## License

This project is for educational purposes. Please respect website terms of service and robots.txt when scraping.

