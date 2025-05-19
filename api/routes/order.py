from fastapi import APIRouter, status, Depends
from fastapi.params import Security
from api.dependencies.auth import get_current_user
from api.repositories.order import OrderRepository
from api.schemas.order import OrderCreate, OrderInDB, OrderInDBWithId
from api.schemas.user import UserScopes
from api.services.db.mongodb.mongo_connection import get_orders_collection
from api.services.order import OrderService
from fastapi import Query
from fastapi import HTTPException

router = APIRouter(prefix="/orders", tags=["Orders"])


async def get_order_service():
    collection = get_orders_collection()
    return OrderService(OrderRepository(collection))


@router.post(
    "/",
    response_model=OrderInDB,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
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
