from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from api.schemas.order import OrderCreate
from api.services.db.mongodb.mongo_connection import (
    connect_mongo,
)


class OrderService:
    def __init__(self):
        self.client: AsyncIOMotorClient = connect_mongo()
        self.db = self.client["elodrinks"]
        self.collection = self.db["orders"]

    async def create_order(self, order_data: OrderCreate) -> dict:
        order_dict = order_data.model_dump()

        result = await self.collection.insert_one(order_dict)
        created_order = await self.collection.find_one({"_id": result.inserted_id})

        created_order["_id"] = str(created_order["_id"])
        return created_order
