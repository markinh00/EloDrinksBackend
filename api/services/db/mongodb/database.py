import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

class MongoDB:
    _instance = None

    def __new__(cls, uri: str = MONGO_URI, db_name: str = MONGO_DATABASE):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, uri: str = MONGO_URI, db_name: str = MONGO_DATABASE):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None

    # func pra conectar
    async def connect(self):
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.db.command("ping")
            print("Successfully connected to MongoDB!")
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    # func pra desconectar
    async def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

    async def get_collection(self, document: str):
        return self.db[document]