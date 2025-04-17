from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from api.models.costumer import Costumer
from api.schemas.costumer import CostumerUpdate
from api.schemas.pagination import CostumerPagination


class CostumerRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, costumer: Costumer) -> Optional[Costumer]:
        try:
            self.session.add(costumer)
            self.session.commit()
            self.session.refresh(costumer)
            return costumer
        except IntegrityError:
            self.session.rollback()
            return None
        except Exception as e:
            raise e

    def get_by_id(self, costumer_id: int) -> Optional[Costumer]:
        return  self.session.get(Costumer, costumer_id)

    def get_by_email(self, costumer_email: str) -> Optional[Costumer]:
        statement = select(Costumer).where(Costumer.email == costumer_email)
        return self.session.exec(statement).first()

    def get_all(self, query: CostumerPagination) -> list[Costumer]:
        statement = select(Costumer).offset((query.page - 1) * query.size).limit(query.size).order_by(query.order.value)
        return list(self.session.exec(statement).all())

    def update(self, costumer_id: int, update_data: CostumerUpdate) -> Optional[Costumer]:
        costumer = self.get_by_id(costumer_id)

        if not costumer:
            return None

        for key, value in update_data.model_dump().items():
            if value is not None:
                setattr(costumer, key, value)

        self.session.add(costumer)
        self.session.commit()
        self.session.refresh(costumer)
        return costumer

    def delete(self, costumer_id: int) -> bool:
        costumer = self.get_by_id(costumer_id)

        if not costumer:
            return False

        self.session.delete(costumer)
        self.session.commit()
        return True
