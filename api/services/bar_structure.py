from typing import List, Optional
from models.bar_structure import BarStructure
from repositories.bar_structure import BarStructureRepository

class BarStructureService:
    def __init__(self):
        self.repository = BarStructureRepository()

    def create_bar(self, name: str, price: float) -> BarStructure:
        new_bar = BarStructure(name=name, price=price)
        return self.repository.create(new_bar)

    def get_bar_by_id(self, bar_id: int) -> Optional[BarStructure]:
        return self.repository.get_by_id(bar_id)

    def get_all_bars(self) -> List[BarStructure]:
        return self.repository.get_all()

    def update_bar(self, bar_id: int, updated_data: dict) -> Optional[BarStructure]:
        return self.repository.update(bar_id, updated_data)

    def delete_bar(self, bar_id: int) -> bool:
        return self.repository.delete(bar_id)