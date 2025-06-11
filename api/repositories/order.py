from pymongo.collection import Collection
from bson import ObjectId

from api.schemas.bar_structure import BarStructureInOrder
from api.schemas.order import DateQueryRange
from api.schemas.product import ProductInOrder


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

    def get_most_ordered_items(self):
        pipeline = [
            {"$match": {"order_status": "confirmed"}},  # Filtra apenas pedidos confirmados
            {"$unwind": "$budget.items"},  # Desconstrói o array de itens
            {
                "$group": {
                    "_id": "$budget.items.id",
                    "name": {"$first": "$budget.items.name"},
                    "total_quantity": {"$sum": "$budget.items.quantity"}
                }
            },
            {"$sort": {"total_quantity": -1}},  # Ordena pelos mais pedidos
            {"$limit": 5},  # Limita aos 5 principais
            {
                "$project": {
                    "_id": 0,
                    "id": "$_id",
                    "name": 1,
                    "quantity": "$total_quantity"
                }
            }
        ]

        results = self.collection.aggregate(pipeline)
        top5_products: list[ProductInOrder] = []

        for result in results:
            top5_products.append(ProductInOrder(
                id=result["id"],
                name=result["name"],
                quantity=result["quantity"],
            ))

        return top5_products

    def get_avg_order_value(self, date_range: DateQueryRange) -> float:
        start_date, end_date = date_range.get_range()

        pipeline = [
            {"$match": {
                "order_status": "confirmed",
                "created_at": {"$gte": start_date, "$lt": end_date}
            }},
            {
                "$group": {
                    "_id": None,
                    "avg_order_value": {"$avg": "$budget.total_value"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "avg_order_value": 1
                }
            }
        ]

        result = list(self.collection.aggregate(pipeline))
        return result[0]["avg_order_value"] if result else 0

    def get_order_count(self, date_range: DateQueryRange) -> int:
        start_date, end_date = date_range.get_range()

        pipeline = [
            {"$match": {
                "order_status": "confirmed",
                "created_at": {"$gte": start_date, "$lt": end_date}
            }},
            {
                "$group": {
                    "_id": None,
                    "order_count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "order_count": 1
                }
            }
        ]

        result = list(self.collection.aggregate(pipeline))
        return result[0]["order_count"] if result else 0

    def get_bar_structure_percentages(self) -> list[BarStructureInOrder]:
        pipeline = [
            {"$match": {"order_status": "confirmed"}},
            {
                "$group": {
                    "_id": {
                        "id": "$budget.bar_structure.id",
                        "name": "$budget.bar_structure.name"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$count"},
                    "bars": {
                        "$push": {
                            "id": "$_id.id",
                            "name": "$_id.name",
                            "count": "$count"
                        }
                    }
                }
            },
            {"$unwind": "$bars"},
            {
                "$project": {
                    "_id": 0,
                    "id": "$bars.id",
                    "name": "$bars.name",
                    "percentage": {
                        "$multiply": [
                            {"$divide": ["$bars.count", "$total"]},
                            100
                        ]
                    }
                }
            }
        ]

        results = list(self.collection.aggregate(pipeline))
        structures: list[BarStructureInOrder] = []

        for result in results:
            structures.append(BarStructureInOrder(
                id=result["id"],
                name=result["name"],
                percentage=result["percentage"]
            ))

        return structures
