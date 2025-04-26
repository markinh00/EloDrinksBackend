from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Security, Query
from starlette.exceptions import HTTPException
from starlette import status
from api.schemas.customer import CustomerRead, CustomerSearchParams, CustomerUpdate
from api.schemas.pagination import CustomerPagination
from api.schemas.user import UserScopes
from api.services.customer import CustomerService
from api.dependencies.auth import get_current_user

router = APIRouter(prefix="/customer", tags=["Customer"])

service = CustomerService()


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer_by_id(
        customer_id: int,
        current_user: Annotated[CustomerRead, Security(get_current_user, scopes=[UserScopes.CUSTOMER.value, UserScopes.ADMIN.value])]
):
    if current_user.data.id != customer_id and current_user.scope != UserScopes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A customer cannot access another customer's data"
        )

    customer = service.get_customer_by_id(customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    return customer


@router.get("/", response_model=list[CustomerRead], dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])])
def get_all_customers(query: Annotated[CustomerPagination, Query()]):
    return service.get_all_customers(query)


@router.get("/search/", dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])], response_model=list[CustomerRead])
def search_customer(search_queries: Annotated[CustomerSearchParams, Query()]):
    return service.search_customer(search_queries)


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
        customer_id: int,
        new_data: CustomerUpdate,
        current_user: Annotated[CustomerRead, Security(get_current_user, scopes=[UserScopes.CUSTOMER.value, UserScopes.ADMIN.value])]
):
    if current_user.data.id != customer_id and current_user.scope != UserScopes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A customer cannot alter another customer's data"
        )

    updated = service.update_customer(customer_id, new_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    return updated


@router.delete("/{customer_id}")
def delete_customer(
        customer_id: int,
        current_user: Annotated[CustomerRead, Security(get_current_user, scopes=[UserScopes.CUSTOMER.value, UserScopes.ADMIN.value])]
):
    if current_user.data.id != customer_id and current_user.scope != UserScopes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A customer cannot delete another customer's data"
        )

    success = service.delete_customer(customer_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    return {"detail": "Customer deleted successfully"}