from enum import Enum


class ActivityName(str, Enum):
    DECIDE_ACTION = "decide_action"
    TAKE_ACTION = "take_action"

    APPEND_MESSAGES_TO_THREAD = "append_messages_to_thread"
    GET_MESSAGES_FROM_THREAD = "get_messages_from_thread"