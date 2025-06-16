import os
from dotenv import load_dotenv
from api.models.product import Product
from api.repositories.product import ProductRepository
from api.schemas.pagination import ProductPagination
from api.schemas.product import ProductCreate, ProductSearchParams, ProductUpdate
from api.services.db.cloudinary.database import Cloudinary
from api.services.db.redis.redis_connection import redis_connection
from api.services.db.sqlmodel.database import get_session

load_dotenv()


class ProductService:
    def __init__(self):
        self.repository = ProductRepository(
            session=get_session(), redis_client=redis_connection()
        )

    async def create_product(self, product: ProductCreate) -> Product | None:
        cloudinary = Cloudinary()
        img_url: str = (
            await cloudinary.upload_image(product.img_file)
            if product.img_file
            else os.getenv("CLOUDINARY_DEFAULT_URL")
        )
        return self.repository.create(
            Product(
                name=product.name,
                price=product.price,
                category=product.category,
                img_url=img_url,
            )
        )

    def search_product(self, search_queries: ProductSearchParams) -> list[Product]:
        return self.repository.search(search_queries)

    def get_all_products(self, query: ProductPagination) -> list[Product]:
        return self.repository.get_all(query)

    def get_all_categories(self) -> list[str]:
        return self.repository.get_all_categories()

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self.repository.get_by_id(product_id)

    async def update_product(self, product_id: int, new_data: ProductUpdate):
        return await self.repository.update(product_id, new_data)

    def delete_product(self, product_id: int) -> bool:
        return self.repository.delete(product_id)
