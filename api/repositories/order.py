import json
import redis
from pymongo.collection import Collection
from bson import ObjectId
from typing import Optional

from api.schemas.bar_structure import BarStructureInOrder
from api.schemas.order import DateQueryRange
from api.schemas.product import ProductInOrder


class OrderRepository:
    def __init__(self, collection: Collection, redis_client: redis.Redis):
        self.collection = collection
        self.redis_client = redis_client
        self.CACHE_TTL_SECONDS = 18000  # 5 hours

    def _invalidate_order_caches(self, order_id: Optional[str] = None):
        """Helper to invalidate order caches."""
        keys_to_delete = self.redis_client.keys("orders:*")
        if keys_to_delete:
            self.redis_client.delete(*keys_to_delete)

        if order_id:
            specific_cache_key = f"order:{order_id}"
            if self.redis_client.exists(specific_cache_key):
                self.redis_client.delete(specific_cache_key)

    def insert_order(self, order_dict: dict) -> ObjectId:
        result = self.collection.insert_one(order_dict)
        self._invalidate_order_caches()
        return result.inserted_id

    def get_order_by_id(self, order_id: ObjectId):
        cache_key = f"order:{str(order_id)}"
        try:
            cached_order_json = self.redis_client.get(cache_key)
            if cached_order_json:
                return json.loads(cached_order_json)
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        order = self.collection.find_one({"_id": order_id})
        if not order:
            return None

        try:
            order_json = json.dumps(order, default=str)
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=order_json
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return order

    def get_all_orders(self, page: int, size: int, deleted: bool):
        cache_key = f"orders:all:page:{page}:size:{size}:deleted:{deleted}"
        try:
            cached_orders_json = self.redis_client.get(cache_key)
            if cached_orders_json:
                return json.loads(cached_orders_json)
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        skip = (page - 1) * size
        query = {} if deleted else {"order_status": {"$ne": "cancelled"}}
        cursor = self.collection.find(query).skip(skip).limit(size)

        orders = list(cursor)

        try:
            orders_json = json.dumps(orders, default=str)
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=orders_json
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return orders

    def get_orders_by_customer_id(
        self, customer_id: int, page: int, size: int, deleted: bool
    ):
        cache_key = (
            f"orders:customer:{customer_id}:page:{page}:size:{size}:deleted:{deleted}"
        )
        try:
            cached_orders_json = self.redis_client.get(cache_key)
            if cached_orders_json:
                return json.loads(cached_orders_json)
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        skip = (page - 1) * size
        query = {"customer.id": customer_id}
        if not deleted:
            query["order_status"] = {"$ne": "cancelled"}

        cursor = self.collection.find(query).skip(skip).limit(size)
        orders = list(cursor)

        try:
            orders_json = json.dumps(orders, default=str)
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=orders_json
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return orders

    def update_status(self, order_id: str, status: str):
        result = self.collection.update_one(
            {"_id": ObjectId(order_id)}, {"$set": {"order_status": status}}
        )
        if result.modified_count == 0:
            raise ValueError("Order not found or status already set to the same value")

        self._invalidate_order_caches(order_id=order_id)

        return self.get_order_by_id(ObjectId(order_id))

    def get_most_ordered_items(self):
        cache_key = "orders:analytics:most_ordered"
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                list_of_dicts = json.loads(cached_data)
                return [ProductInOrder.model_validate(d) for d in list_of_dicts]
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        pipeline = [
            {"$match": {"order_status": "confirmed"}},
            {"$unwind": "$budget.items"},
            {
                "$group": {
                    "_id": "$budget.items.id",
                    "name": {"$first": "$budget.items.name"},
                    "total_quantity": {"$sum": "$budget.items.quantity"},
                }
            },
            {"$sort": {"total_quantity": -1}},
            {"$limit": 5},
            {
                "$project": {
                    "_id": 0,
                    "id": "$_id",
                    "name": 1,
                    "quantity": "$total_quantity",
                }
            },
        ]
        results = self.collection.aggregate(pipeline)
        top5_products = [ProductInOrder(**result) for result in results]

        try:
            data_to_cache = json.dumps([p.model_dump() for p in top5_products])
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=data_to_cache
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return top5_products

    def get_avg_order_value(self, date_range: DateQueryRange) -> float:
        start_date, end_date = date_range.get_range()

        start_date_key = start_date.strftime("%Y-%m-%d")
        end_date_key = end_date.strftime("%Y-%m-%d")
        cache_key = (
            f"orders:analytics:avg_value:start:{start_date_key}:end:{end_date_key}"
        )

        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return float(cached_data)
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        pipeline = [
            {
                "$match": {
                    "order_status": "confirmed",
                    "created_at": {"$gte": start_date, "$lt": end_date},
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_order_value": {"$avg": "$budget.total_value"},
                }
            },
            {"$project": {"_id": 0, "avg_order_value": 1}},
        ]
        result = list(self.collection.aggregate(pipeline))
        avg_value = result[0]["avg_order_value"] if result else 0.0

        try:
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=str(avg_value)
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return avg_value

    def get_order_count(self, date_range: DateQueryRange) -> int:
        start_date, end_date = date_range.get_range()

        start_date_key = start_date.strftime("%Y-%m-%d")
        end_date_key = end_date.strftime("%Y-%m-%d")
        cache_key = f"orders:analytics:count:start:{start_date_key}:end:{end_date_key}"

        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return int(cached_data)
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        pipeline = [
            {
                "$match": {
                    "order_status": "confirmed",
                    "created_at": {"$gte": start_date, "$lt": end_date},
                }
            },
            {"$group": {"_id": None, "order_count": {"$sum": 1}}},
            {"$project": {"_id": 0, "order_count": 1}},
        ]
        result = list(self.collection.aggregate(pipeline))
        count = result[0]["order_count"] if result else 0

        try:
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=str(count)
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return count

    def get_bar_structure_percentages(self) -> list[BarStructureInOrder]:
        cache_key = "orders:analytics:bar_percentages"
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                list_of_dicts = json.loads(cached_data)
                return [BarStructureInOrder.model_validate(d) for d in list_of_dicts]
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        pipeline = [
            {"$match": {"order_status": "confirmed"}},
            {
                "$group": {
                    "_id": {
                        "id": "$budget.bar_structure.id",
                        "name": "$budget.bar_structure.name",
                    },
                    "count": {"$sum": 1},
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
                            "count": "$count",
                        }
                    },
                }
            },
            {"$unwind": "$bars"},
            {
                "$project": {
                    "_id": 0,
                    "id": "$bars.id",
                    "name": "$bars.name",
                    "percentage": {
                        "$multiply": [{"$divide": ["$bars.count", "$total"]}, 100]
                    },
                }
            },
        ]
        results = list(self.collection.aggregate(pipeline))
        structures = [BarStructureInOrder(**result) for result in results]

        try:
            data_to_cache = json.dumps([s.model_dump() for s in structures])
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=data_to_cache
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return structures
