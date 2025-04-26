from typing import Annotated
from fastapi.params import Query
from starlette import status
from starlette.exceptions import HTTPException
from api.models.product import Product
from api.schemas.pagination import ProductPagination
from api.schemas.product import ProductCreate, ProductSearchParams, ProductRead, ProductUpdate
from api.services.product import ProductService
from fastapi import APIRouter, Form, UploadFile


router = APIRouter(
    prefix="/product",
    tags=["product"]
)

service = ProductService()

@router.post("/", response_model=ProductRead)
async def create_product(
        name: str = Form(...),
        price: float = Form(...),
        category: str = Form(...),
        img_file: UploadFile | None = None
) -> Product:
    new_product = ProductCreate(name=name, price=price, category=category, img_file=img_file)
    result = await service.create_product(new_product)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="could not create the product"
        )

    return result


@router.get("/", response_model=list[ProductRead])
def get_all_products(query: Annotated[ProductPagination, Query()]):
    return  service.get_all_products(query)


@router.get("/search", response_model=list[ProductRead])
def search_products(search_queries: Annotated[ProductSearchParams, Query()]):
    return service.search_product(search_queries)


@router.get("/categories", response_model=list[str])
def get_all_distinct_categories():
    return service.repository.get_all_categories()


@router.get("/{product_id}", response_model=ProductRead | None)
def get_product_by_id(product_id: int):
    result = service.get_product_by_id(product_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found"
        )

    return  result


@router.put("/{product_id}")
async def update_product(
        product_id: int,
        name: str | None = Form(default=None),
        price: float | None = Form(default=None),
        category: str | None = Form(default=None),
        img_file: UploadFile | None = Form(default=None),
        delete_img: bool | None = Form(default=None),
):
    new_data = ProductUpdate(name=name, price=price, category=category, img_file=img_file, delete_img=delete_img)
    updated = await service.update_product(product_id, new_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found")

    return updated


@router.delete("/{product_id}")
def delete_product(product_id: int):
    success = service.delete_product(product_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found")

    return {"detail": "Customer deleted successfully"}