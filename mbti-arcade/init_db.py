import asyncio
from app.core.db import init_db
from app.core.models_db import SQLModel

async def main():
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 