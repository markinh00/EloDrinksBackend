from fastapi import HTTPException
from pydantic import BaseModel, model_validator
from typing import List, Optional, Self
from starlette import status

from sqlmodel import Field
from api.schemas.product import ProductInPack


class PackCreate(BaseModel):
    name: str
    event_type: str
    guest_count: int
    price: float
    structure_id: Optional[int] = None
    products: List[ProductInPack]


class PackRead(BaseModel):
    id: int
    name: str
    event_type: str
    guest_count: int
    price: float
    structure_id: Optional[int] = None
    products: List[ProductInPack]

    class Config:
        from_attributes = True


class PackUpdate(BaseModel):
    name: str
    event_type: str
    guest_count: int
    price: float
    structure_id: Optional[int] = None
    products: Optional[List[ProductInPack]] = None


class PackSearchParams(BaseModel):
    name: str | None = Field(default=None)
    event_type: str | None = Field(default=None)
    guest_count: int | None = Field(default=None)
    price: float | None = Field(default=None)
    product_name: str | None = Field(default=None)

    @model_validator(mode="after")
    def validate_field(self) -> Self:
        counter: int = 0
        for field, _ in self.model_dump().items():
            if self.model_dump()[field] is not None:
                counter = counter + 1
            if counter >= 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="only one parameter can be used for search!",
                )
        if counter == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="a parameter is needed for the search!",
            )
        return self


class PackWithoutProductsRead(BaseModel):
    id: int
    name: str
    event_type: str
    guest_count: int
    price: float
    structure_id: Optional[int] = None

    class Config:
        from_attributes = True
