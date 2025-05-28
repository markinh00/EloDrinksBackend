from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.models.notification import Notification
from api.schemas.notification import NotificationCreate, NotificationUpdate
from datetime import datetime


class NotificationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: NotificationCreate) -> Optional[Notification]:
        try:
            notification = Notification.model_validate(data)
            self.session.add(notification)
            self.session.commit()
            self.session.refresh(notification)
            return notification
        except IntegrityError:
            self.session.rollback()
            return None
        except Exception as e:
            self.session.rollback()
            raise e

    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        return self.session.get(Notification, notification_id)

    def get_all(self, page: int, size: int) -> List[Notification]:
        offset = (page - 1) * size
        statement = select(Notification).offset(offset).limit(size)
        return list(self.session.exec(statement).all())

    def update(
        self, notification_id: int, data: NotificationUpdate
    ) -> Optional[Notification]:
        notification = self.get_by_id(notification_id)

        if not notification:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(notification, key, value)

        notification.updated_at = datetime.now()

        try:
            self.session.add(notification)
            self.session.commit()
            self.session.refresh(notification)
            return notification
        except IntegrityError:
            self.session.rollback()
            return None
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, notification_id: int) -> bool:
        notification = self.get_by_id(notification_id)

        if not notification:
            return False

        self.session.delete(notification)
        self.session.commit()
        return True
