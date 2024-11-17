from enum import Enum


class ActivityName(str, Enum):
    # Action loop activities
    DECIDE_ACTION = "decide_action"
    TAKE_ACTION = "take_action"

    # Agent state activities
    APPEND_MESSAGES_TO_THREAD = "append_messages_to_thread"
    GET_MESSAGES_FROM_THREAD = "get_messages_from_thread"
    ADD_ARTIFACT_TO_CONTEXT = "add_artifact_to_context"

    # Notification activities
    SEND_NOTIFICATION = "send_notification"

    # LLM activities
    ASK_LLM = "ask_llm"
