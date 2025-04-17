from typing import List, Optional

from starlette.exceptions import HTTPException
from starlette import status
from api.models.costumer import Costumer
from api.repositories.costumer import CostumerRepository
from api.schemas.costumer import CostumerRegister, CostumerUpdate
from api.schemas.pagination import CostumerPagination
from api.services.db.sqlmodel.database import get_session


class CostumerService:
    def __init__(self):
        self.repository = CostumerRepository(session=get_session())

    def create_costumer(self, costumer_data: CostumerRegister) -> Costumer:
        try:
            new_Costumer = Costumer(
                name=costumer_data.name,
                email=costumer_data.email,
                telephone=costumer_data.telephone,
                password=costumer_data.password
            )
            return self.repository.create(new_Costumer)
        except AttributeError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{error}"
            )
        except Exception as e:
            raise e

    def get_costumer_by_id(self, costumer_id: int) -> Optional[Costumer]:
        return self.repository.get_by_id(costumer_id)

    def get_costumer_by_email(self, costumer_email: str) -> Optional[Costumer]:
        return self.repository.get_by_email(costumer_email)

    def get_all_costumers(self, query: CostumerPagination) -> List[Costumer]:
        return self.repository.get_all(query)

    def update_costumer(self, costumer_id: int, updated_data: CostumerUpdate) -> Optional[Costumer]:
        return self.repository.update(costumer_id, updated_data)

    def delete_costumer(self, costumer_id: int) -> bool:
        return self.repository.delete(costumer_id)
