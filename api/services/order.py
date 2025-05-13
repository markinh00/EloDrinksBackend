from datetime import datetime
from api.schemas.order import OrderCreate, OrderInDB
from api.repositories.order import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    async def create_order(self, order: OrderCreate) -> OrderInDB:
        now = datetime.now()
        order_dict = order.model_dump()
        order_dict["created_at"] = now
        order_dict["updated_at"] = now

        inserted_id = await self.repository.insert_order(order_dict)
        order_in_db = await self.repository.get_order_by_id(inserted_id)
        return order_in_db

    async def get_all_orders(self, page: int, size: int) -> list[OrderInDB]:
        orders = await self.repository.get_all_orders(page=page, size=size)
        return [OrderInDB(**order) for order in orders]

    async def get_orders_by_customer_id(
        self, customer_id: int, page: int, size: int
    ) -> list[OrderInDB]:
        orders = await self.repository.get_orders_by_customer_id(
            customer_id=customer_id, page=page, size=size
        )
        return [OrderInDB(**order) for order in orders]
