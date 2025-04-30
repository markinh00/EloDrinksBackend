from fastapi import APIRouter, HTTPException, Query
from typing import List
from fastapi.params import Security
from api.dependencies.auth import get_current_user
from api.schemas.user import UserScopes
from api.services.sale import SaleService
from api.schemas.sale import (
    SaleCreate,
    SaleRead,
    SaleUpdate,
)

router = APIRouter(prefix="/sales", tags=["Sales"])
service = SaleService()


@router.post(
    "/",
    response_model=SaleRead,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])]
)
def create_sale(sale_data: SaleCreate):
    return service.create_sale(sale_data)


@router.get(
    "/",
    response_model=List[SaleRead],
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value])]
)
def get_all_sales(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    return service.get_all_sales(page=page, size=size)


@router.get(
    "/search",
    response_model=List[SaleRead],
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value])]
)
def search_sales(name: str):
    return service.search_sales(name=name)


@router.get(
    "/{sale_id}",
    response_model=SaleRead,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value])]
)
def get_sale_by_id(sale_id: int):
    sale = service.get_sale_by_id(sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.put(
    "/{sale_id}",
    response_model=SaleRead,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])]
)
def update_sale(sale_id: int, updated_data: SaleUpdate):
    updated = service.update_sale(sale_id, updated_data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Sale not found")
    return updated


@router.delete(
    "/{sale_id}",
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])]
)
def delete_sale(sale_id: int):
    success = service.delete_sale(sale_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sale not found")
    return {"detail": "Sale deleted successfully"}
