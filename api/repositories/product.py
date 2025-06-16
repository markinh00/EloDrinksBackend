import os
import json
import redis
from typing import Optional  # Importar List e Optional
from dotenv import load_dotenv
from sqlmodel import Session, select, desc, distinct
from api.models.product import Product
from sqlalchemy.exc import IntegrityError
from api.schemas.pagination import ProductPagination
from api.schemas.product import ProductSearchParams, ProductUpdate
from api.services.db.cloudinary.database import Cloudinary

load_dotenv()


class ProductRepository:
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis_client = redis_client
        self.CACHE_TTL_SECONDS = 18000  # 5 hours

    def _invalidate_product_caches(self, product_id: Optional[int] = None):
        """Helper to invalidate product caches."""
        list_cache_keys = self.redis_client.keys("products:*")
        if list_cache_keys:
            self.redis_client.delete(*list_cache_keys)

        if product_id:
            specific_cache_key = f"product:{product_id}"
            if self.redis_client.exists(specific_cache_key):
                self.redis_client.delete(specific_cache_key)

    def create(self, product: Product) -> Product | None:
        try:
            self.session.add(product)
            self.session.commit()
            self.session.refresh(product)
            self._invalidate_product_caches()
            return product
        except IntegrityError as e:
            self.session.rollback()
            return None
        except Exception as e:
            raise e

    def search(self, params: ProductSearchParams) -> list[Product]:
        cache_key = f"products:search:{params.model_dump_json()}"
        try:
            cached_products_json = self.redis_client.get(cache_key)
            if cached_products_json:
                cached_products = json.loads(cached_products_json)
                return [Product.model_validate(p) for p in cached_products]
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        filters = []
        for key, value in params.model_dump(exclude_unset=True).items():
            filters.append(getattr(Product, key).contains(value))

        statement = select(Product).where(*filters)
        products = self.session.exec(statement).all()

        try:
            products_json = json.dumps([p.model_dump() for p in products])
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=products_json
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return products

    def get_all(self, query: ProductPagination) -> list[Product]:
        cache_key = f"products:page:{query.page}:size:{query.size}:order:{query.order.value}:desc:{query.desc}"
        try:
            cached_products_json = self.redis_client.get(cache_key)
            if cached_products_json:
                cached_products = json.loads(cached_products_json)
                return [Product.model_validate(p) for p in cached_products]
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        statement = (
            select(Product)
            .offset((query.page - 1) * query.size)
            .limit(query.size)
            .order_by(desc(query.order.value) if query.desc else query.order.value)
        )
        products = list(self.session.exec(statement).all())

        try:
            products_json = json.dumps([p.model_dump() for p in products])
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=products_json
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return products

    def get_all_categories(self) -> list[str]:
        cache_key = "products:categories"
        try:
            cached_categories_json = self.redis_client.get(cache_key)
            if cached_categories_json:
                return json.loads(cached_categories_json)
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        statement = select(distinct(Product.category))
        categories = list(self.session.exec(statement).all())

        try:
            categories_json = json.dumps(categories)
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=categories_json
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return categories

    def get_by_id(self, product_id: int) -> Product | None:
        cache_key = f"product:{product_id}"
        try:
            cached_product_json = self.redis_client.get(cache_key)
            if cached_product_json:
                return Product.model_validate_json(cached_product_json)
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        product = self.session.get(Product, product_id)
        if not product:
            return None

        try:
            product_json = product.model_dump_json()
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=product_json
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return product

    async def update(self, product_id: int, new_data: ProductUpdate) -> Product | None:
        try:
            product = self.get_by_id(product_id)

            if not product:
                return None

            cloudinary = Cloudinary()

            for key, value in new_data.model_dump(exclude_unset=True).items():
                if key == "delete_img":
                    cloudinary.delete_image(product.img_url)
                    product.img_url = os.getenv("CLOUDINARY_DEFAULT_URL")
                elif key == "img_file":
                    cloudinary.delete_image(product.img_url)
                    img_url: str = await cloudinary.upload_image(value)
                    product.img_url = img_url
                else:
                    setattr(product, key, value)

            self.session.add(product)
            self.session.commit()
            self.session.refresh(product)

            self._invalidate_product_caches(product_id=product_id)

            return product
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, product_id: int) -> bool:
        product = self.session.get(Product, product_id)

        if not product:
            return False

        cloudinary = Cloudinary()
        cloudinary.delete_image(product.img_url)

        self.session.delete(product)
        self.session.commit()

        self._invalidate_product_caches(product_id=product_id)

        return True
