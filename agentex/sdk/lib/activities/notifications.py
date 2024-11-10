from temporalio import activity

from agentex.sdk.lib.activities.names import ActivityName
from agentex.src.adapters.notifications.port import NotificationPort
from agentex.src.entities.notifications import NotificationRequest


class NotificationActivities:

    def __init__(self, notification_gateway: NotificationPort):
        super().__init__()
        self.notification_gateway = notification_gateway

    @activity.defn(name=ActivityName.SEND_NOTIFICATION)
    async def send_notification(self, notification: NotificationRequest) -> None:
        await self.notification_gateway.send(notification=notification)
