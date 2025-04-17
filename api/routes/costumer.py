from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Security, Query
from starlette.exceptions import HTTPException
from starlette import status
from api.schemas.costumer import CostumerRead, CostumerUpdate
from api.schemas.pagination import CostumerPagination
from api.schemas.user import UserScopes
from api.services.costumer import CostumerService
from dependencies import get_current_user

router = APIRouter(prefix="/costumer", tags=["Costumer"])

service = CostumerService()

@router.get("/id/{costumer_id}", response_model=CostumerRead)
def get_user_by_id(
        costumer_id: int,
        current_user: Annotated[CostumerRead, Security(get_current_user, scopes=[UserScopes.COSTUMER.value, UserScopes.ADMIN.value])]
):
    if current_user.data.id != costumer_id and current_user.scope != UserScopes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A costumer cannot access another costumer's data"
        )

    costumer = service.get_costumer_by_id(costumer_id)

    if not costumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    return costumer

@router.get("/email/{costumer_email}", response_model=CostumerRead)
def get_user_by_email(
        costumer_email: str,
        current_user: Annotated[CostumerRead, Security(get_current_user, scopes=[UserScopes.COSTUMER.value, UserScopes.ADMIN.value])]
):
    if current_user.data.email != costumer_email and current_user.scope != UserScopes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A costumer cannot access another costumer's data"
        )

    costumer = service.get_costumer_by_email(costumer_email)

    if not costumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    return costumer

@router.get("/", response_model=list[CostumerRead], dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])])
def get_all_costumers(query: Annotated[CostumerPagination, Query()]):
    return service.get_all_costumers(query)

@router.put("/{costumer_id}", response_model=CostumerRead)
def update_costumer(
        costumer_id: int,
        new_data: CostumerUpdate,
        current_user: Annotated[CostumerRead, Security(get_current_user, scopes=[UserScopes.COSTUMER.value, UserScopes.ADMIN.value])]
):
    if current_user.data.id != costumer_id and current_user.scope != UserScopes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A costumer cannot alter another costumer's data"
        )

    updated = service.update_costumer(costumer_id, new_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    return updated

@router.delete("/{costumer_id}")
def delete_costumer(
        costumer_id: int,
        current_user: Annotated[CostumerRead, Security(get_current_user, scopes=[UserScopes.COSTUMER.value, UserScopes.ADMIN.value])]
):
    if current_user.data.id != costumer_id and current_user.scope != UserScopes.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A costumer cannot delete another costumer's data"
        )

    success = service.delete_costumer(costumer_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    return {"detail": "Costumer deleted successfully"}