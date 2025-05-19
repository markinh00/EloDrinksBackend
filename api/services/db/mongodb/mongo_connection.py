import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

client = None


def get_orders_collection():
    global client
    try:
        if client is None:
            client = MongoClient(MONGO_URI)

        db = client[MONGO_DATABASE]
        collection = db["orders"]
        logging.info("Synchronous connection successfully established.")
        return collection
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise
