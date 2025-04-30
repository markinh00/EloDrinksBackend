from typing import List, Optional
from sqlmodel import Session, select
from api.models.sale import Sale


class SaleRepository:
    def __init__(self, session: Session):
        self.session: Session = session

    def create(self, sale: Sale) -> Sale:
        self.session.add(sale)
        self.session.commit()
        self.session.refresh(sale)
        return sale

    def get_by_id(self, sale_id: int) -> Optional[Sale]:
        return self.session.get(Sale, sale_id)

    def get_all(self, page: int = 1, size: int = 10) -> List[Sale]:
        offset = (page - 1) * size
        statement = select(Sale).offset(offset).limit(size)
        return self.session.exec(statement).all()

    def search_by_name(self, name: str) -> List[Sale]:
        statement = select(Sale).where(Sale.name.ilike(f"%{name}%"))
        return self.session.exec(statement).all()

    def update(self, sale_id: int, updated_data: dict) -> Optional[Sale]:
        sale = self.get_by_id(sale_id)
        if not sale:
            return None
        for key, value in updated_data.items():
            setattr(sale, key, value)
        self.session.add(sale)
        self.session.commit()
        self.session.refresh(sale)
        return sale

    def delete(self, sale_id: int) -> bool:
        sale = self.get_by_id(sale_id)
        if not sale:
            return False
        self.session.delete(sale)
        self.session.commit()
        return True
