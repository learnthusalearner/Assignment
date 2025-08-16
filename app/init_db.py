import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.models.db import engine, Base

async def init_models():
    """Create all database tables"""
    print("🔧 Initializing database...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(" Database tables created successfully!")
        print(" Tables: brands, products")
    except Exception as e:
        print(f" Failed to initialize database: {e}")
        return False
    return True

async def main():
    """Main function"""
    success = await init_models()
    if success:
        print(" Database initialization complete!")
    else:
        print(" Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())