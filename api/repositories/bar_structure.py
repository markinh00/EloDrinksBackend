from sqlmodel import Session, select
from typing import Optional, List
from models import BarStructure

class BarStructureRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, bar_structure: BarStructure) -> BarStructure:
        self.session.add(bar_structure)
        self.session.commit()
        self.session.refresh(bar_structure)
        return bar_structure

    def get_by_id(self, bar_id: int) -> Optional[BarStructure]:
        return self.session.get(BarStructure, bar_id)

    def get_all(self) -> List[BarStructure]:
        statement = select(BarStructure)
        return self.session.exec(statement).all()

    def update(self, bar_id: int, updated_data: dict) -> Optional[BarStructure]:
        bar_structure = self.get_by_id(bar_id)
        if not bar_structure:
            return None
        for key, value in updated_data.items():
            setattr(bar_structure, key, value)
        self.session.add(bar_structure)
        self.session.commit()
        self.session.refresh(bar_structure)
        return bar_structure

    def delete(self, bar_id: int) -> bool:
        bar_structure = self.get_by_id(bar_id)
        if not bar_structure:
            return False
        self.session.delete(bar_structure)
        self.session.commit()
        return True
