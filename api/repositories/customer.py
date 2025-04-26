from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, desc
from api.models.customer import Customer
from api.schemas.customer import CustomerUpdate, CustomerSearchParams
from api.schemas.pagination import CustomerPagination


class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, customer: Customer) -> Optional[Customer]:
        try:
            self.session.add(customer)
            self.session.commit()
            self.session.refresh(customer)
            return customer
        except IntegrityError:
            self.session.rollback()
            return None
        except Exception as e:
            raise e

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        return  self.session.get(Customer, customer_id)

    def get_by_email(self, customer_email: str) -> Optional[Customer]:
        try:
            statement = select(Customer).where(Customer.email == customer_email)
            return self.session.exec(statement).first()
        except Exception as e:
            self.session.rollback()
            raise e

    def search(self, params: CustomerSearchParams) -> list[Customer]:
        for key, value in params.model_dump().items():
            if value is not None:
                statement = select(Customer).where(getattr(Customer, key).contains(value))
        return self.session.exec(statement).all()

    def get_all(self, query: CustomerPagination) -> list[Customer]:
        statement = (select(Customer)
                     .offset((query.page - 1) * query.size)
                     .limit(query.size)
                     .order_by(desc(query.order.value) if query.desc else query.order.value))
        return list(self.session.exec(statement).all())

    def update(self, customer_id: int, update_data: CustomerUpdate) -> Optional[Customer]:
        customer = self.get_by_id(customer_id)

        if not customer:
            return None

        for key, value in update_data.model_dump().items():
            if value is not None:
                setattr(customer, key, value)

        self.session.add(customer)
        self.session.commit()
        self.session.refresh(customer)
        return customer

    def delete(self, customer_id: int) -> bool:
        customer = self.get_by_id(customer_id)

        if not customer:
            return False

        self.session.delete(customer)
        self.session.commit()
        return True
