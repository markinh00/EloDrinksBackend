from typing import Optional, List

from api.repositories.notification import NotificationRepository
from api.schemas.notification import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
)
from api.services.db.sqlmodel.database import get_session


class NotificationService:
    def __init__(self):
        self.session = get_session()
        self.repository = NotificationRepository(session=self.session)

    def create_notification(self, data: NotificationCreate) -> NotificationRead:
        return self.repository.create(data)

    def get_notification(self, notification_id: int) -> Optional[NotificationRead]:
        return self.repository.get_by_id(notification_id)

    def list_notifications(self, page: int, size: int) -> List[NotificationRead]:
        return self.repository.get_all(page, size)

    def update_notification(
        self, notification_id: int, data: NotificationUpdate
    ) -> Optional[NotificationRead]:
        return self.repository.update(notification_id, data)

    def delete_notification(self, notification_id: int) -> bool:
        return self.repository.delete(notification_id)
