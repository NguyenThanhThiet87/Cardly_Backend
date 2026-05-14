import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_connection = MongoDB()

async def connect_to_mongo():
    # Create a new client and connect to the server
    db_connection.client = AsyncIOMotorClient(MONGO_URI)
    db_connection.db = db_connection.client[DB_NAME]
    print("--- Đã kết nối tới MongoDB ---")

async def close_mongo_connection():
    db_connection.client.close()
    print("--- Đã đóng kết nối MongoDB ---")

async def get_db():
    if db_connection.db is None:
        await connect_to_mongo()
    return db_connection.db
