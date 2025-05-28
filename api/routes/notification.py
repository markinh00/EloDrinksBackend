from fastapi import APIRouter, HTTPException, Security, status

from api.dependencies.auth import get_current_user
from api.schemas.notification import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
)
from api.schemas.user import UserScopes
from api.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
service = NotificationService()


@router.post(
    "/",
    response_model=NotificationRead,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
    status_code=status.HTTP_201_CREATED,
)
def create_notification(data: NotificationCreate):
    result = service.create_notification(data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create notification",
        )

    return result


@router.get(
    "/{notification_id}",
    response_model=NotificationRead,
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
)
def get_notification(notification_id: int):
    notification = service.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.get(
    "/customer/{customer_id}",
    response_model=list[NotificationRead],
    dependencies=[
        Security(
            get_current_user, scopes=[UserScopes.ADMIN.value, UserScopes.CUSTOMER.value]
        )
    ],
)
async def list_notifications_by_customer(
    customer_id: int,
    page: int = 1,
    size: int = 10,
):
    return service.list_notifications_by_customer(customer_id, page, size)


@router.patch(
    "/{notification_id}",
    response_model=NotificationRead,
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
)
def update_notification(
    notification_id: int,
    data: NotificationUpdate,
):
    notification = service.update_notification(notification_id, data)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@router.delete(
    "/{notification_id}",
    dependencies=[Security(get_current_user, scopes=[UserScopes.ADMIN.value])],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: int,
):
    success = service.delete_notification(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")

    return success
