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


class PackRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, pack: Pack) -> Pack:
        try:
            self.session.add(pack)
            self.session.flush()
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

        return PackRead(
            id=pack.id,
            name=pack.name,
            event_type=pack.event_type,
            guest_count=pack.guest_count,
            price=pack.price,
            structure_id=pack.structure_id,
            products=product_list,
        )

    def get_by_id_without_products(
        self, pack_id: int
    ) -> Optional[PackWithoutProductsRead]:
        pack = self.session.get(Pack, pack_id)
        if not pack:
            return None

        return pack

    def get_all(self, page: int = 1, size: int = 10) -> List[PackRead]:
        try:
            offset = (page - 1) * size
            statement = select(Pack).offset(offset).limit(size)
            return self.session.exec(statement).all()
        except Exception as e:
            self.session.rollback()
            raise e

    def search(self, params: PackSearchParams) -> List[Pack]:
        for key, value in params.model_dump().items():
            if value is not None:
                if key == "product_name":
                    product_ids = self.session.exec(
                        select(Product.id)
                        .distinct()
                        .where(Product.name.contains(value))
                    ).all()
                    statement = select(Pack).where(
                        Pack.products.any(PackHasProduct.product_id.in_(product_ids))
                    )
                else:
                    statement = select(Pack).where(getattr(Pack, key).contains(value))
        return self.session.exec(statement).all()

    def update(self, pack_id: int, updated_data: PackUpdate) -> Optional[Pack]:
        pack = self.get_by_id(pack_id)
        if not pack:
            return None

        pack_columns = set(c_attr.key for c_attr in inspect(Pack).mapper.column_attrs)

        for key, value in updated_data.model_dump(exclude_unset=True).items():
            if key in pack_columns:
                setattr(pack, key, value)

        self.session.add(pack)
        self.session.commit()
        self.session.refresh(pack)
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
        return True
