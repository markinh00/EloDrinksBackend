from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId


class OrderRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def insert_order(self, order_dict: dict) -> ObjectId:
        result = await self.collection.insert_one(order_dict)
        return result.inserted_id

    async def get_order_by_id(self, order_id: ObjectId):
        return await self.collection.find_one({"_id": order_id})

    async def get_all_orders(self, page: int, size: int):
        skip = (page - 1) * size
        cursor = self.collection.find().skip(skip).limit(size)
        orders = []
        async for order in cursor:
            orders.append(order)
        return orders
