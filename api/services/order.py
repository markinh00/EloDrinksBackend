from bson import ObjectId
from api.helpers.timezone import get_current_time_utc_minus_3
from api.schemas.order import OrderCreate, OrderInDB, OrderInDBWithId, DateQueryRange, OrderStatistics
from api.repositories.order import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create_order(self, order: OrderCreate) -> OrderInDB:
        now = get_current_time_utc_minus_3()
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

    def get_orders_statistics(self):
        ordersStatistics = OrderStatistics(
            top5_items= self.repository.get_most_ordered_items(),
            avg_order_value= self.repository.get_avg_order_value(date_range=DateQueryRange()),
            month_order_count= self.repository.get_order_count(date_range=DateQueryRange()),
            bar_structure_percentage= self.repository.get_bar_structure_percentages()
        )
        return ordersStatistics