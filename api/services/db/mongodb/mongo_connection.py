import logging
import os
from dotenv import load_dotenv
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
import asyncio

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

_client = None


def get_mongo_client():
    global _client
    if _client is None:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        _client = AsyncIOMotorClient(MONGO_URI)
    return _client


async def get_orders_collection() -> AsyncIOMotorCollection:
    try:
        client = get_mongo_client()
        db: AsyncIOMotorDatabase = client[MONGO_DATABASE]
        collection: AsyncIOMotorCollection = db["orders"]
        logging.info("Asynchronous connection successfully established.")
        return collection
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise
