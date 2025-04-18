from pydantic import BaseModel, Field
from enum import Enum


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=10, le=100)

class CustomerOrderEnum(Enum):
    ID = "id"
    NAME = "name"
    TELEPHONE = "telephone"
    EMAIL = "email"

class CustomerPagination(Pagination):
    order: CustomerOrderEnum = Field(default=CustomerOrderEnum.NAME)
