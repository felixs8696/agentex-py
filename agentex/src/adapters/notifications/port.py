from abc import ABC, abstractmethod

from agentex.src.entities.notifications import NotificationRequest, Notification


class NotificationPort(ABC):

    @abstractmethod
    async def send(self, notification: NotificationRequest) -> Notification:
        raise NotImplementedError

