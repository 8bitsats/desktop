import motor.motor_asyncio
from src.config import settings

class MongoDB:
    client = None
    db = None

async def initialize_db():
    MongoDB.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
    MongoDB.db = MongoDB.client.get_default_database()

async def shutdown_db():
    if MongoDB.client:
        MongoDB.client.close() 