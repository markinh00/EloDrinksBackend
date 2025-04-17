import os
from datetime import datetime, timezone, timedelta
from typing import Annotated
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Security, Depends
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, SecurityScopes
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException
from jose import JWTError, jwt
from api.models.admin import Admin
from api.models.costumer import Costumer
from api.schemas.jwt_token import TokenData
from api.schemas.user import UserScopes, User
from api.services.admin import AdminService
from api.services.costumer import CostumerService

load_dotenv()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes={
        UserScopes.ADMIN.value: "Access to all urls",
        UserScopes.COSTUMER.value: "Access to limited urls"
    },
)

admin_service = AdminService()
costumer_service = CostumerService()

async def get_api_key(X_API_Key: str = Security(api_key_header)):
    if X_API_Key == os.getenv("API_KEY"):
        return X_API_Key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API KEY"
        )


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str, scope: UserScopes) -> Admin | Costumer | bool:
    user: Admin | Costumer | None = None

    if scope == UserScopes.ADMIN.value:
        user = admin_service.get_admin_by_email(email)
    elif scope == UserScopes.COSTUMER.value:
        user = costumer_service.get_costumer_by_email(email)

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, email=email)
    except (JWTError, ValidationError):
        raise credentials_exception

    for scope in token_data.scopes:
        if scope not in security_scopes.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    user: Admin | Costumer | None = None
    current_user_scope: UserScopes | None = None

    if token_data.scopes[0] == UserScopes.ADMIN.value:
        user = admin_service.get_admin_by_email(email)
        current_user_scope = UserScopes.ADMIN
    elif token_data.scopes[0] == UserScopes.COSTUMER.value:
        user = costumer_service.get_costumer_by_email(email)
        current_user_scope = UserScopes.COSTUMER

    if user is None:
        raise credentials_exception

    return User(data=user, scope=current_user_scope)


def decode_reset_password_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        scopes: str = payload.get("scopes")

        return {"email": email, "scopes": scopes}
    except JWTError:
        return None