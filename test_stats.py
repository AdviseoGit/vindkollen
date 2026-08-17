import asyncio
import os
import json
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("No DATABASE_URL set")
    exit(0)

# Replace asyncpg driver specifically required for SQLAlchemy
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DATABASE_URL, echo=False)

async def check():
    try:
        async with engine.connect() as conn:
            # Query last 7 days
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            query_7d = text("SELECT COUNT(*) FROM vindkollen_leads WHERE created_at >= :start")
            res_7d = await conn.execute(query_7d, {"start": seven_days_ago})
            last_7_days = res_7d.scalar()
            
            # Query total
            query_total = text("SELECT COUNT(*) FROM vindkollen_leads")
            res_total = await conn.execute(query_total)
            total = res_total.scalar()
            
            print(json.dumps({"total": total, "last_7_days": last_7_days}))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check())
