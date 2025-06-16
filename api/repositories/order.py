from pymongo.collection import Collection
from bson import ObjectId


class OrderRepository:
    def __init__(self, collection: Collection):
        self.collection = collection

    def insert_order(self, order_dict: dict) -> ObjectId:
        result = self.collection.insert_one(order_dict)
        return result.inserted_id

    def get_order_by_id(self, order_id: ObjectId):
        return self.collection.find_one({"_id": order_id})

    def get_all_orders(self, page: int, size: int, deleted: bool):
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
        for order in cursor:
            orders.append(order)
        return orders

    def get_orders_by_customer_id(
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
        for order in cursor:
            orders.append(order)
        return orders

    def update_status(self, order_id: str, status: str):
        result = self.collection.update_one(
            {"_id": ObjectId(order_id)}, {"$set": {"order_status": status}}
        )
        if result.modified_count == 0:
            raise ValueError("Order not found or status already set to the same value")
        return self.get_order_by_id(ObjectId(order_id))

    def update_order(self, order_id: ObjectId, order_update_dict: dict):
        result = self.collection.update_one(
            {"_id": order_id}, {"$set": order_update_dict}
        )
        if result.modified_count == 0:
            raise ValueError("Order not found or no changes made")
        return self.get_order_by_id(order_id)

    def delete_order(self, order_id: ObjectId):
        result = self.collection.find_one_and_delete({"_id": order_id})
        if not result:
            raise ValueError("Order not found")
        return result
