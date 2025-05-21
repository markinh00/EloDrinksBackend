from datetime import datetime

from bson import ObjectId
from api.schemas.order import OrderCreate, OrderInDB, OrderInDBWithId
from api.repositories.order import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create_order(self, order: OrderCreate) -> OrderInDB:
        now = datetime.now()
        order_dict = order.model_dump()
        order_dict["created_at"] = now
        order_dict["updated_at"] = now

        inserted_id = self.repository.insert_order(order_dict)
        order_in_db = self.repository.get_order_by_id(inserted_id)
        return order_in_db

    def get_all_orders(
        self, page: int, size: int, deleted: bool
    ) -> list[OrderInDBWithId]:
        orders = self.repository.get_all_orders(page=page, size=size, deleted=deleted)
        return [
            OrderInDBWithId(**{**order, "_id": str(order["_id"])}) for order in orders
        ]

    def get_orders_by_customer_id(
        self, customer_id: int, page: int, size: int, deleted: bool
    ) -> list[OrderInDBWithId]:
        orders = self.repository.get_orders_by_customer_id(
            customer_id=customer_id, page=page, size=size, deleted=deleted
        )
        return [
            OrderInDBWithId(**{**order, "_id": str(order["_id"])}) for order in orders
        ]

    def get_order_by_id(self, order_id: str) -> OrderInDBWithId | None:
        order_object_id = ObjectId(order_id)
        order = self.repository.get_order_by_id(order_object_id)
        if order:
            return OrderInDBWithId(**{**order, "_id": str(order["_id"])})
        return None

    def cancel_order(self, order_id: str) -> OrderInDB:
        return self.repository.update_status(order_id, "cancelled")

    def confirm_order(self, order_id: str) -> OrderInDB:
        return self.repository.update_status(order_id, "confirmed")
