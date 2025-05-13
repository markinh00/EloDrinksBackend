from fastapi import APIRouter, status
from api.repositories.order import OrderRepository
from api.schemas.order import OrderCreate, OrderInDB, OrderInDBWithId
from api.services.db.mongodb.mongo_connection import (
    get_orders_collection,
)
from api.services.order import OrderService
from fastapi import Query
from fastapi import HTTPException

router = APIRouter(prefix="/orders", tags=["Orders"])

collection = get_orders_collection()
service = OrderService(OrderRepository(collection))


@router.post("/", response_model=OrderInDB, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
):
    return await service.create_order(order)


@router.get("/", response_model=list[OrderInDBWithId])
async def get_orders(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    return await service.get_all_orders(page=page, size=size)


@router.get("/customer/{customer_id}", response_model=list[OrderInDBWithId])
async def get_orders_by_customer_id(
    customer_id: int, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)
):
    return await service.get_orders_by_customer_id(customer_id, page=page, size=size)


@router.patch("/{order_id}/cancel", response_model=OrderInDB)
async def cancel_order(order_id: str):
    try:
        return await service.cancel_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
