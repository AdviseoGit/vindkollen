import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.schema import CreateTable
import main

async def test_db():
    print("Testing DB connection...")
    
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("No DATABASE_URL found. Will test with local sqlite for verification")
        db_url = "sqlite+aiosqlite:///leads.db"
        
    engine = create_async_engine(db_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(main.Base.metadata.create_all)
        print("Created tables")

if __name__ == "__main__":
    asyncio.run(test_db())
