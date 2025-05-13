import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

client = MongoClient(MONGO_URI, maxPoolSize=50, minPoolSize=5)


def connect_mongo(collection_name: str = "orders") -> tuple[Collection]:
    try:
        db: Database = client[MONGO_DATABASE]
        collection: Collection = db[collection_name]
        print("Conexão estabelecida com sucesso.")
        return collection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise
