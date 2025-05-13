from fastapi import APIRouter, status
from api.repositories.order import OrderRepository
from api.schemas.order import OrderCreate, OrderInDB
from api.services.db.mongodb.mongo_connection import (
    get_orders_collection,
)
from api.services.order import OrderService
from fastapi import Query

router = APIRouter(prefix="/orders", tags=["Orders"])

collection = get_orders_collection()


@router.post("/", response_model=OrderInDB, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
):
    service = OrderService(OrderRepository(collection))
    return await service.create_order(order)


@router.get("/", response_model=list[OrderInDB])
async def get_orders(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    service = OrderService(OrderRepository(collection))
    return await service.get_all_orders(page=page, size=size)
