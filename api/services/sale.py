from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from api.models.sale import Sale
from api.schemas.sale import SaleCreate
from api.repositories.sale import SaleRepository
from api.services.db.sqlmodel.database import get_session


class SaleService:
    def __init__(self):
        self.repository = SaleRepository(session=get_session())

    def create_sale(self, data: SaleCreate) -> Sale:
        sale = Sale(**data.model_dump())
        try:
            return self.repository.create(sale)
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="Invalid foreign key: product_id or pack_id does not exist",
            )

    def get_all_sales(self, page: int = 1, size: int = 10) -> List[Sale]:
        return self.repository.get_all(page=page, size=size)

    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        return self.repository.get_by_id(sale_id)

    def search_sales(self, name: str) -> List[Sale]:
        return self.repository.search_by_name(name)

    def update_sale(self, sale_id: int, updated_data: dict) -> Optional[Sale]:
        return self.repository.update(sale_id, updated_data)

    def delete_sale(self, sale_id: int) -> bool:
        return self.repository.delete(sale_id)
