from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from api.schemas.order import OrderCreate
from api.services.db.mongodb.mongo_connection import (
    connect_mongo,
)

BR_TZ = timezone(timedelta(hours=-3))


class OrderRepository:
    def __init__(self):
        self.client: AsyncIOMotorClient = connect_mongo()
        self.db = self.client["elodrinks"]
        self.collection = self.db["orders"]

    async def create(self, order_data: OrderCreate) -> dict:
        order_dict = order_data.model_dump()
        order_dict["created_at"] = datetime.now(timezone.utc).astimezone(BR_TZ)
        order_dict["updated_at"] = datetime.now(timezone.utc).astimezone(BR_TZ)

        result = await self.collection.insert_one(order_dict)
        created_order = await self.collection.find_one({"_id": result.inserted_id})

        if created_order:
            created_order["_id"] = str(created_order["_id"])
        return created_order
