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

    async def get_all_orders(self, page: int, size: int, deleted: bool):
        skip = (page - 1) * size
        if deleted:
            cursor = self.collection.find().skip(skip).limit(size)
        else:
            cursor = (
                self.collection.find({"order_status": {"$ne": "cancelled"}})
                .skip(skip)
                .limit(size)
            )
        orders = []
        async for order in cursor:
            orders.append(order)
        return orders

    async def get_orders_by_customer_id(
        self, customer_id: int, page: int, size: int, deleted: bool
    ):
        skip = (page - 1) * size
        if deleted:
            cursor = (
                self.collection.find({"customer.id": customer_id})
                .skip(skip)
                .limit(size)
            )
        else:
            cursor = (
                self.collection.find(
                    {"customer.id": customer_id, "order_status": {"$ne": "cancelled"}}
                )
                .skip(skip)
                .limit(size)
            )
        orders = []
        async for order in cursor:
            orders.append(order)
        return orders

    async def update_status(self, order_id: str, status: str):
        result = await self.collection.update_one(
            {"_id": ObjectId(order_id)}, {"$set": {"order_status": status}}
        )
        if result.modified_count == 0:
            raise ValueError("Order not found or status already set to the same value")
        return await self.get_order_by_id(ObjectId(order_id))
