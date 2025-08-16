# app/services/http.py

import httpx
from bs4 import BeautifulSoup

async def fetch_html(url: str) -> str:
    """
    Fetch HTML content from a given URL asynchronously.
    """
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"[ERROR] Failed to fetch HTML from {url}: {e}")
        return ""


async def fetch_json(url: str) -> dict:
    """
    Fetch JSON response from a given API endpoint asynchronously.
    """
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch JSON from {url}: {e}")
        return {}
