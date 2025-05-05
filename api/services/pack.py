from typing import List, Optional

from fastapi import HTTPException
from sqlmodel import select
from api.models.pack import Pack
from api.models.product import Product
from api.schemas.pack import PackCreate, PackUpdate
from api.repositories.pack import PackRepository
from api.services.db.sqlmodel.database import get_session


class PackService:
    def __init__(self):
        self.session = get_session()
        self.repository = PackRepository(session=self.session)

    def create_pack(self, data: PackCreate) -> Pack:
        products = self.session.exec(
            select(Product).where(Product.id.in_(data.product_ids))
        ).all()

        if len(products) != len(data.product_ids):
            raise HTTPException(status_code=400, detail="Some product_ids are invalid")

        pack = Pack(**data.model_dump())
        pack = self.repository.create(pack)
        self.repository.add_products_to_pack(pack.id, data.product_ids)
        self.session.commit()
        self.session.refresh(pack)
        return pack

    def get_all_packs(self, page: int = 1, size: int = 10) -> List[Pack]:
        return self.repository.get_all(page=page, size=size)

    def get_pack_by_id(self, pack_id: int) -> Optional[Pack]:
        return self.repository.get_by_id(pack_id)

    def search_packs(self, name: str) -> List[Pack]:
        return self.repository.search_by_name(name)

    def update_pack(self, pack_id: int, updated_data: PackUpdate) -> Optional[Pack]:
        if updated_data.product_ids:
            products = self.session.exec(
                select(Product).where(Product.id.in_(updated_data.product_ids))
            ).all()

            if len(products) != len(updated_data.product_ids):
                raise HTTPException(
                    status_code=400, detail="Some product_ids are invalid"
                )

        pack = self.repository.update(pack_id, updated_data)
        if not pack:
            return None

        if updated_data.product_ids is not None:
            self.repository.remove_all_products_from_pack(pack_id)
            self.repository.add_products_to_pack(pack_id, updated_data.product_ids)

        self.session.commit()
        self.session.refresh(pack)
        return pack

    def delete_pack(self, pack_id: int) -> bool:
        return self.repository.delete(pack_id)
