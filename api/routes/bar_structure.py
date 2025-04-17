from fastapi import APIRouter, HTTPException, Query
from typing import List

from api.services.bar_structure import BarStructureService
from api.schemas.bar_structure import (
    BarStructureCreate,
    BarStructureRead,
    BarStructureUpdate,
)

router = APIRouter(prefix="/structure", tags=["Structure"])
service = BarStructureService()


@router.post("/", response_model=BarStructureRead)
def create_bar_structure(bar_data: BarStructureCreate):
    return service.create_bar(name=bar_data.name, price=bar_data.price)


@router.get("/", response_model=List[BarStructureRead])
def get_all_bar_structures(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    return service.get_all_bars(page=page, size=size)


@router.get("/{bar_id}", response_model=BarStructureRead)
def get_bar_structure(bar_id: int):
    bar = service.get_bar_by_id(bar_id)
    if not bar:
        raise HTTPException(status_code=404, detail="BarStructure not found")
    return bar


@router.put("/{bar_id}", response_model=BarStructureRead)
def update_bar_structure(bar_id: int, updated_data: BarStructureUpdate):
    updated = service.update_bar(bar_id, updated_data.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="BarStructure not found")
    return updated


@router.delete("/{bar_id}")
def delete_bar_structure(bar_id: int):
    success = service.delete_bar(bar_id)
    if not success:
        raise HTTPException(status_code=404, detail="BarStructure not found")
    return {"detail": "BarStructure deleted successfully"}
