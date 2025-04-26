from pydantic import BaseModel, Field
from enum import Enum


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=10, le=100)
    desc: bool | None = Field(default=None)

class CustomerOrderEnum(Enum):
    ID = "id"
    NAME = "name"
    TELEPHONE = "telephone"
    EMAIL = "email"

class CustomerPagination(Pagination):
    order: CustomerOrderEnum = Field(default=CustomerOrderEnum.NAME)

class ProductOrderEnum(Enum):
    ID = "id"
    NAME = "name"
    PRICE = "price"
    CATEGORY = "category"
    IMG = "img_url"

class ProductPagination(Pagination):
    order: ProductOrderEnum = Field(default=ProductOrderEnum.NAME)
