
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings

async def check_residents():
    print(f"Connecting to MongoDB at {settings.MONGODB_URL}")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    count = await db.residents.count_documents({})
    print(f"Total residents in DB: {count}")
    
    cursor = db.residents.find({})
    residents = await cursor.to_list(length=100)
    
    for r in residents:
        print(f"Resident: {r.get('resident_name')} - Code: {r.get('resident_code')} - Active: {r.get('is_active')}")

if __name__ == "__main__":
    asyncio.run(check_residents())
