import requests

from agentex.src.adapters.notifications.port import NotificationPort
from agentex.src.entities.notifications import NotificationRequest, Notification

NTFY_BASE_URL = "https://ntfy.sh/"


class NtfyGateway(NotificationPort):

    async def send(self, notification: NotificationRequest) -> Notification:
        response = requests.post(
            url=NTFY_BASE_URL,
            data=notification.to_json(),
        )
        return Notification.from_dict(response.json())
