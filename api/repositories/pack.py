from typing import List, Optional
from sqlmodel import select, Session
from api.models.pack import Pack


class PackRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, pack: Pack) -> Pack:
        self.session.add(pack)
        self.session.commit()
        self.session.refresh(pack)
        return pack

    def get_by_id(self, pack_id: int) -> Optional[Pack]:
        return self.session.get(Pack, pack_id)

    def get_all(self, page: int = 1, size: int = 10) -> List[Pack]:
        offset = (page - 1) * size
        statement = select(Pack).offset(offset).limit(size)
        return self.session.exec(statement).all()

    def search_by_name(self, name: str) -> List[Pack]:
        statement = select(Pack).where(Pack.name.ilike(f"%{name}%"))
        return self.session.exec(statement).all()

    def update(self, pack_id: int, updated_data: dict) -> Optional[Pack]:
        pack = self.get_by_id(pack_id)
        if not pack:
            return None
        for key, value in updated_data.items():
            setattr(pack, key, value)
        self.session.add(pack)
        self.session.commit()
        self.session.refresh(pack)
        return pack

    def delete(self, pack_id: int) -> bool:
        pack = self.get_by_id(pack_id)
        if not pack:
            return False
        self.session.delete(pack)
        self.session.commit()
        return True
