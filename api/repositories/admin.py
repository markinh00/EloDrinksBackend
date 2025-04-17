from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from api.schemas.admin import AdminUpdate
from api.models.admin import Admin

class AdminRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, admin: Admin) -> Optional[Admin]:
        try:
            self.session.add(admin)
            self.session.commit()
            self.session.refresh(admin)
            return admin
        except IntegrityError:
            self.session.rollback()
            return None
        except Exception as e:
            raise e

    def get_by_id(self, admin_id: int) -> Optional[Admin]:
        return  self.session.get(Admin, admin_id)

    def get_by_email(self, admin_email: str) -> Optional[Admin]:
        statement = select(Admin).where(Admin.email == admin_email)
        return self.session.exec(statement).first()

    def get_all(self) -> list[Admin]:
        statement = select(Admin)
        return list(self.session.exec(statement).all())

    def update(self, admin_id: int, update_data: AdminUpdate) -> Optional[Admin]:
        admin = self.get_by_id(admin_id)

        if not admin:
            return None

        for key, value in update_data.model_dump():
            if value is not None: setattr(admin, key, value)

        self.session.add(admin)
        self.session.commit()
        self.session.refresh(admin)
        return admin

    def delete(self, admin_id: int) -> bool:
        admin = self.get_by_id(admin_id)

        if not admin:
            return False

        self.session.delete(admin)
        self.session.commit()
        return True
