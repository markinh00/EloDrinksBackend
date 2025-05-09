from typing import List, Optional
from sqlmodel import delete, inspect, select, Session
from api.models.pack import Pack
from api.models.pack_product import PackHasProduct
from api.schemas.pack import PackUpdate
from api.schemas.product import ProductInPack


class PackRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, pack: Pack) -> Pack:
        self.session.add(pack)
        self.session.flush()
        return pack

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

    def get_by_id(self, pack_id: int) -> Optional[Pack]:
        return self.session.get(Pack, pack_id)

    def get_all(self, page: int = 1, size: int = 10) -> List[Pack]:
        offset = (page - 1) * size
        statement = select(Pack).offset(offset).limit(size)
        return self.session.exec(statement).all()

    def search_by_name(self, name: str) -> List[Pack]:
        statement = select(Pack).where(Pack.name.ilike(f"%{name}%"))
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

        pack = self.get_by_id(pack_id)
        if not pack:
            return False

        self.session.delete(pack)
        self.session.commit()
        return True
