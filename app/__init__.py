from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="Gen-AI Shopify Insights", version="1.0.0")
app.include_router(api_router)
