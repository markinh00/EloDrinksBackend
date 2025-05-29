import json
from typing import List, Optional
from sqlmodel import delete, inspect, select, Session
from api.models.pack import Pack
from api.models.pack_product import PackHasProduct
from api.models.product import Product
from api.schemas.pack import (
    PackRead,
    PackSearchParams,
    PackUpdate,
    PackWithoutProductsRead,
)
from api.schemas.product import ProductInPack
from sqlalchemy import and_
import redis


class PackRepository:
    def __init__(self, session: Session, redis_client: redis.Redis):
        self.session = session
        self.redis_client = redis_client
        self.CACHE_TTL_SECONDS = 18000  # 5 hours

    def create(self, pack: Pack) -> Pack:
        try:
            self.session.add(pack)
            self.session.flush()
            keys = self.redis_client.keys("packs:page:*")
            if keys:
                self.redis_client.delete(*keys)
            return pack
        except Exception as e:
            self.session.rollback()
            raise e

    def add_products_to_pack(self, pack_id: int, products: List[ProductInPack]) -> None:
        relations = [
            PackHasProduct(
                pack_id=pack_id, product_id=product.id, quantity=product.quantity
            )
            for product in products
        ]
        self.session.add_all(relations)

    def remove_all_products_from_pack(self, pack_id: int) -> None:
        self.session.exec(
            delete(PackHasProduct).where(PackHasProduct.pack_id == pack_id)
        )

    def get_by_id(self, pack_id: int) -> Optional[PackRead]:
        cache_key = f"pack:{pack_id}"

        try:
            cached_pack_json = self.redis_client.get(cache_key)
            if cached_pack_json:
                return PackRead.model_validate_json(cached_pack_json)
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        # If not found in cache, fetch from database
        pack = self.session.get(Pack, pack_id)
        if not pack:
            return None

        results = self.session.exec(
            select(Product.id, PackHasProduct.quantity)
            .join(PackHasProduct, Product.id == PackHasProduct.product_id)
            .where(PackHasProduct.pack_id == pack_id)
        ).all()

        product_list = [
            ProductInPack(id=prod_id, quantity=qty) for prod_id, qty in results
        ]

        pack_to_return = PackRead(
            id=pack.id,
            name=pack.name,
            event_type=pack.event_type,
            guest_count=pack.guest_count,
            price=pack.price,
            structure_id=pack.structure_id,
            products=product_list,
        )

        try:
            pack_json_to_cache = pack_to_return.model_dump_json()
            self.redis_client.setex(
                name=cache_key, time=self.CACHE_TTL_SECONDS, value=pack_json_to_cache
            )
        except redis.RedisError as e:
            print(f"Redis error setting {cache_key}: {e}")

        return pack_to_return

    def get_by_id_without_products(
        self, pack_id: int
    ) -> Optional[PackWithoutProductsRead]:
        pack = self.session.get(Pack, pack_id)
        if not pack:
            return None

        return pack

    def get_all(self, page: int = 1, size: int = 10) -> List[PackRead]:
        cache_key = f"packs:page:{page}:size:{size}"
        try:
            cached_packs_json = self.redis_client.get(cache_key)
            if cached_packs_json:
                cached_packs = json.loads(cached_packs_json)
                if cached_packs:
                    return [
                        PackWithoutProductsRead.model_validate(pack)
                        for pack in cached_packs
                    ]
        except redis.RedisError as e:
            print(f"Redis error accessing {cache_key}: {e}")

        # If not found in cache, fetch from database
        try:
            offset = (page - 1) * size
            statement = select(Pack).offset(offset).limit(size)
            packs = self.session.exec(statement).all()
            if packs:
                list_of_packs_dict = [p.model_dump() for p in packs]
                packs_json = json.dumps(list_of_packs_dict)
                self.redis_client.setex(
                    name=cache_key, time=self.CACHE_TTL_SECONDS, value=packs_json
                )
            return packs
        except Exception as e:
            self.session.rollback()
            raise e

    def search(self, params: PackSearchParams) -> List[PackRead]:
        filters = []

        for key, value in params.model_dump().items():
            if value is not None:
                if key == "product_name":
                    product_ids = self.session.exec(
                        select(Product.id).where(Product.name.contains(value))
                    ).all()
                    filters.append(PackHasProduct.product_id.in_(product_ids))
                else:
                    filters.append(getattr(Pack, key).contains(value))

        if params.product_name:
            statement = select(Pack).join(PackHasProduct).where(and_(*filters))
        else:
            statement = select(Pack).where(and_(*filters))

        packs = self.session.exec(statement).all()

        result = []
        for pack in packs:
            products = self.session.exec(
                select(Product, PackHasProduct.quantity)
                .join(PackHasProduct, Product.id == PackHasProduct.product_id)
                .where(PackHasProduct.pack_id == pack.id)
            ).all()

            product_in_packs = [
                ProductInPack(id=product.id, quantity=quantity)
                for product, quantity in products
            ]

            pack_read = PackRead(
                id=pack.id,
                name=pack.name,
                event_type=pack.event_type,
                guest_count=pack.guest_count,
                price=pack.price,
                structure_id=pack.structure_id,
                products=product_in_packs,
            )
            result.append(pack_read)

        return result

    def update(self, pack_id: int, updated_data: PackUpdate) -> Optional[Pack]:
        pack = self.get_by_id_without_products(pack_id)
        if not pack:
            return None

        pack_columns = set(c_attr.key for c_attr in inspect(Pack).mapper.column_attrs)

        for key, value in updated_data.model_dump(exclude_unset=True).items():
            if key in pack_columns:
                setattr(pack, key, value)

        self.session.add(pack)
        self.session.commit()
        self.session.refresh(pack)
        if self.redis_client.exists(f"pack:{pack_id}"):
            self.redis_client.delete(f"pack:{pack_id}")
            keys = self.redis_client.keys("packs:page:*")
            if keys:
                self.redis_client.delete(*keys)
        return pack

    def delete(self, pack_id: int) -> bool:
        self.session.exec(
            delete(PackHasProduct).where(PackHasProduct.pack_id == pack_id)
        )

        pack = self.get_by_id_without_products(pack_id)
        if not pack:
            return False

        self.session.delete(pack)
        self.session.commit()
        if self.redis_client.exists(f"pack:{pack_id}"):
            self.redis_client.delete(f"pack:{pack_id}")
            keys = self.redis_client.keys("packs:page:*")
            if keys:
                self.redis_client.delete(*keys)
        return True
