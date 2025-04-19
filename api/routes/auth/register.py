import os
from datetime import timedelta
from dotenv import load_dotenv
from fastapi import APIRouter
from starlette.exceptions import HTTPException
from starlette import status
from api.models.admin import Admin
from api.models.costumer import Costumer
from api.schemas.admin import AdminRegister
from api.schemas.jwt_token import Token
from api.schemas.costumer import CostumerRegister
from api.schemas.user import UserScopes
from api.services.admin import AdminService
from api.services.costumer import CostumerService
from dependencies import create_access_token, get_password_hash

router = APIRouter(prefix="/register", tags=["Auth"])

admin_service = AdminService()
user_service = CostumerService()

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

@router.post("/", response_model=Token)
def register_user(role: UserScopes, user_data: AdminRegister | CostumerRegister) -> Token:
    try:
        result: Admin | Costumer | None = None

        if user_data.password != user_data.confirmPassword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="'password' and 'confirmPassword' must be the same value!"
            )

        user_data.password = get_password_hash(user_data.password)

        if role == UserScopes.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="a admin cannot be registered using this route!"
            )
        elif role == UserScopes.COSTUMER:
            result = user_service.create_costumer(user_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user_data.email} already exists!",
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": result.email}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        raise e
