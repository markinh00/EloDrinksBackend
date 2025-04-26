from typing import List, Optional
from api.models.pack import Pack
from api.schemas.pack import PackCreate, PackUpdate
from api.repositories.pack import PackRepository
from api.services.db.sqlmodel.database import get_session


class PackService:
    def __init__(self):
        self.repository = PackRepository(session=get_session())

    def create_pack(self, data: PackCreate) -> Pack:
        pack = Pack(**data.model_dump())
        return self.repository.create(pack)

    def get_all_packs(self, page: int = 1, size: int = 10) -> List[Pack]:
        return self.repository.get_all(page=page, size=size)

    def get_pack_by_id(self, pack_id: int) -> Optional[Pack]:
        return self.repository.get_by_id(pack_id)

    def search_packs(self, name: str) -> List[Pack]:
        return self.repository.search_by_name(name)

    def update_pack(self, pack_id: int, updated_data: PackUpdate) -> Optional[Pack]:
        return self.repository.update(pack_id, updated_data)

    def delete_pack(self, pack_id: int) -> bool:
        return self.repository.delete(pack_id)
