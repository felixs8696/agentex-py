from enum import Enum


class SignalName(str, Enum):
    INSTRUCT = "instruct"
    APPROVE = "approve"


class QueryName(str, Enum):
    GET_EVENT_LOG = "get_event_log"
