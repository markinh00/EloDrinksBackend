from fastapi import APIRouter, status, Depends
from fastapi.params import Security
from api.dependencies.auth import get_current_user
from api.repositories.order import OrderRepository
from api.schemas.order import OrderCreate, OrderInDB, OrderInDBWithId, OrderStatistics
from api.schemas.user import UserScopes
from api.services.db.mongodb.mongo_connection import get_orders_collection
from api.services.db.redis.redis_connection import redis_connection
from api.services.order import OrderService
from fastapi import Query
from fastapi import HTTPException

router = APIRouter(prefix="/orders", tags=["Orders"])


async def get_order_service():
    collection = get_orders_collection()
    return OrderService(OrderRepository(collection, redis_connection()))


@router.post(
    "/",
    response_model=OrderInDB,
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    order: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    return service.create_order(order)


@router.get(
    "/",
    response_model=list[OrderInDBWithId],
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
)
async def get_orders(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    deleted: bool = False,
    service: OrderService = Depends(get_order_service),
):
    return service.get_all_orders(page=page, size=size, deleted=deleted)


@router.get(
    "/statistics",
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
    response_model=OrderStatistics,
)
async def get_orders_statistics(
    service: OrderService = Depends(get_order_service),
):
    return service.get_orders_statistics()


@router.get(
    "/{order_id}",
    response_model=OrderInDBWithId,
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
)
async def get_order_by_id(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    order = service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order


@router.get(
    "/customer/{customer_id}",
    response_model=list[OrderInDBWithId],
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
)
async def get_orders_by_customer_id(
    customer_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    deleted: bool = False,
    service: OrderService = Depends(get_order_service),
):
    return service.get_orders_by_customer_id(
        customer_id, page=page, size=size, deleted=deleted
    )


@router.patch(
    "/{order_id}/cancel",
    response_model=OrderInDB,
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
)
async def cancel_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    try:
        return service.cancel_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch(
    "/{order_id}/confirm",
    response_model=OrderInDB,
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
)
async def confirm_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    try:
        return service.confirm_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{order_id}/update",
    response_model=OrderInDB,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
)
async def update_order(
    order_id: str,
    order: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    try:
        return service.update_order(order_id, order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{order_id}",
    response_model=OrderInDB,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
)
async def delete_order(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    try:
        return service.delete_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
