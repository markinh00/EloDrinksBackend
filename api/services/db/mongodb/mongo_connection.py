import logging
import os
from dotenv import load_dotenv
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

client = AsyncIOMotorClient(MONGO_URI)


def get_orders_collection() -> AsyncIOMotorCollection:
    try:
        db: AsyncIOMotorDatabase = client[MONGO_DATABASE]
        collection: AsyncIOMotorCollection = db["orders"]
        logging.info("Asynchronous connection successfully established.")
        return collection
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise
