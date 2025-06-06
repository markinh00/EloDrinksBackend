from fastapi import APIRouter, HTTPException, Query
from typing import List
from fastapi.params import Security
from api.dependencies.auth import get_current_user
from api.schemas.user import UserScopes
from api.services.bar_structure import BarStructureService
from api.schemas.bar_structure import (
    BarStructureCreate,
    BarStructureRead,
    BarStructureUpdate,
)

router = APIRouter(prefix="/structure", tags=["Structure"])
service = BarStructureService()


@router.post("/", response_model=BarStructureRead, dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])])
def create_bar_structure(bar_data: BarStructureCreate):
    return service.create_bar(name=bar_data.name, price=bar_data.price)


@router.get("/", response_model=List[BarStructureRead], dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value])])
def get_all_bar_structures(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    return service.get_all_bars(page=page, size=size)


@router.get("/search", response_model=List[BarStructureRead], dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value])])
def search_bar_structures(name: str):
    return service.search_bars(name=name)


@router.get("/{bar_id}", response_model=BarStructureRead, dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value])])
def get_bar_structure(bar_id: int):
    bar = service.get_bar_by_id(bar_id)
    if not bar:
        raise HTTPException(status_code=404, detail="BarStructure not found")
    return bar


@router.put("/{bar_id}", response_model=BarStructureRead, dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])])
def update_bar_structure(bar_id: int, updated_data: BarStructureUpdate):
    updated = service.update_bar(bar_id, updated_data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="BarStructure not found")
    return updated


@router.delete("/{bar_id}", dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])])
def delete_bar_structure(bar_id: int):
    success = service.delete_bar(bar_id)
    if not success:
        raise HTTPException(status_code=404, detail="BarStructure not found")
    return {"detail": "BarStructure deleted successfully"}

