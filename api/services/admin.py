from typing import List, Optional
from api.models.admin import Admin
from api.repositories.admin import AdminRepository
from api.schemas.admin import AdminUpdate, AdminRegister
from api.services.db.sqlmodel.database import get_session


class AdminService:
    def __init__(self):
        self.repository = AdminRepository(session=get_session())

    def create_admin(self, admin_data: AdminRegister) -> Admin:
        new_admin = Admin(name=admin_data.name, email=admin_data.email, password=admin_data.password)
        return self.repository.create(new_admin)

    def get_admin_by_id(self, admin_id: int) -> Optional[Admin]:
        return self.repository.get_by_id(admin_id)

    def get_admin_by_email(self, admin_email: str) -> Optional[Admin]:
        return self.repository.get_by_email(admin_email)

    def get_all_admins(self) -> List[Admin]:
        return self.repository.get_all()

    def update_admin(self, admin_id: int, updated_data: AdminUpdate) -> Optional[Admin]:
        return self.repository.update(admin_id, updated_data)

    def delete_admin(self, admin_id: int) -> bool:
        return self.repository.delete(admin_id)
