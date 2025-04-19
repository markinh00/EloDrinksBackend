from enum import Enum
from pydantic import BaseModel
from api.models.admin import Admin
from api.models.customer import Customer


class UserScopes(Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"

class User(BaseModel):
    data: Admin | Customer
    scope: UserScopes