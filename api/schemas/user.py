from enum import Enum

from pydantic import BaseModel

from api.models.admin import Admin
from api.models.costumer import Costumer


class UserScopes(Enum):
    ADMIN = "admin"
    COSTUMER = "costumer"

class User(BaseModel):
    data: Admin | Costumer
    scope: UserScopes