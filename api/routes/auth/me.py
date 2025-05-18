from typing import Annotated
from fastapi import APIRouter, Security
from api.dependencies.auth import get_current_user
from api.schemas.admin import AdminRead
from api.schemas.customer import CustomerRead
from api.schemas.user import User, UserScopes

router = APIRouter(prefix="/me", tags=["Auth"])


@router.get("/", response_model=AdminRead | CustomerRead)
def get_current_user(
        current_user: Annotated[User, Security(get_current_user, scopes=[UserScopes.CUSTOMER.value, UserScopes.ADMIN.value])]
):
    return current_user.data
