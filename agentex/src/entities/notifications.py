from typing import Optional, List

from pydantic import Field

from agentex.utils.model_utils import BaseModel


class Action(BaseModel):
    action: str = Field(..., description="Action name")
    label: str = Field(..., description="Action label")
    url: str = Field(..., description="Action URL")
    clear: Optional[bool] = Field(False, description="Clear notification after action button is tapped")


class NotificationRequest(BaseModel):
    topic: str = Field(..., description="Target topic name")
    message: Optional[str] = Field("👋 Hello there", description="Message body")
    title: Optional[str] = Field("Notification", description="Message title")
    tags: Optional[List[str]] = Field(["notification"], description="List of tags that may or not map to emojis")
    priority: Optional[int] = Field(3, description="Message priority with 1=min, 3=default and 5=max")
    actions: Optional[List[Action]] = Field(
        default_factory=list, description="Custom user action buttons for notifications"
    )
    click: Optional[str] = Field(None, description="Website opened when notification is clicked")
    attach: Optional[str] = Field(None, description="URL of an attachment")
    markdown: Optional[bool] = Field(True, description="Set to true if the message is Markdown-formatted")
    icon: Optional[str] = Field(None, description="URL to use as notification icon")
    filename: Optional[str] = Field(None, description="File name of the attachment")
    delay: Optional[str] = Field(None, description="Timestamp or duration for delayed delivery")
    email: Optional[str] = Field(None, description="E-mail address for e-mail notifications")
    call: Optional[str] = Field(None, description="Phone number to use for voice call")


class Attachment(BaseModel):
    name: str = Field(..., description="Name of the attachment")
    url: str = Field(..., description="URL of the attachment")
    type: Optional[str] = Field(None, description="Mime type of the attachment")
    size: Optional[int] = Field(None, description="Size of the attachment in bytes")
    expires: Optional[int] = Field(None, description="Attachment expiry date as Unix time stamp")


class Notification(BaseModel):
    id: str = Field(..., description="Randomly chosen message identifier")
    time: int = Field(..., description="Message date time, as Unix time stamp")
    expires: Optional[int] = Field(None, description="Unix time stamp indicating when the message will be deleted")
    event: str = Field(..., description="Message type, typically you'd be only interested in message")
    topic: str = Field(..., description="Comma-separated list of topics the message is associated with")
    message: str = Field(..., description="Message body")
    title: Optional[str] = Field(None, description="Message title")
    tags: Optional[List[str]] = Field(None, description="List of tags that may or not map to emojis")