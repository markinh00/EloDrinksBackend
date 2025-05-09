from fastapi import APIRouter, HTTPException, Query
from typing import Annotated, List
from fastapi.params import Security

from api.dependencies.auth import get_current_user
from api.schemas.user import UserScopes
from api.schemas.pack import (
    PackCreate,
    PackRead,
    PackSearchParams,
    PackUpdate,
)
from api.services.pack import PackService

router = APIRouter(prefix="/packs", tags=["Packs"])
service = PackService()


@router.post(
    "/",
    response_model=PackRead,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
)
def create_pack(pack_data: PackCreate):
    return service.create_pack(pack_data)


@router.get(
    "/",
    response_model=List[PackRead],
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
)
def get_all_packs(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    return service.get_all_packs(page=page, size=size)


@router.get(
    "/search",
    response_model=List[PackRead],
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
)
def search_packs(search_queries: Annotated[PackSearchParams, Query()]):
    return service.search_packs(search_queries)


@router.get(
    "/{pack_id}",
    response_model=PackRead,
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
)
def get_pack(pack_id: int):
    pack = service.get_pack_by_id(pack_id)
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")
    return pack


@router.put(
    "/{pack_id}",
    response_model=PackRead,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
)
def update_pack(pack_id: int, updated_data: PackUpdate):
    updated = service.update_pack(pack_id, updated_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Pack not found")
    return updated


@router.delete(
    "/{pack_id}",
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
)
def delete_pack(pack_id: int):
    success = service.delete_pack(pack_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pack not found")
    return {"detail": "Pack deleted successfully"}
