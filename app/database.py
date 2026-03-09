import motor.motor_asyncio
from app.config import settings

client: motor.motor_asyncio.AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.DB_NAME]
    print(f"Connected to MongoDB => {settings.DB_NAME}")

async def close_db():
    global client
    if client:
        client.close()
        print("MongoDB closed")

def get_db():
    return db