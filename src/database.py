import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(override=True)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")


class MongoDB:
    client: AsyncIOMotorClient = None
    db = None


db_connection = MongoDB()


async def connect_to_mongo():
    db_name = os.getenv("DB_NAME")
    print(f"--- Connecting to MongoDB, DB_NAME={db_name} ---")
    db_connection.client = AsyncIOMotorClient(MONGO_URI)
    db_connection.db = db_connection.client[db_name]
    print("--- Connected to MongoDB ---")


async def close_mongo_connection():
    db_connection.client.close()
    print("--- Disconnected from MongoDB ---")


async def get_db():
    if db_connection.db is None:
        await connect_to_mongo()
    return db_connection.db
