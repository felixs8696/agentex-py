from enum import Enum

AGENT_NAME = "doc-writer"
TASK_QUEUE_NAME = "doc_writer_task_queue"


class ActionRegistryKey(str, Enum):
    WRITER = "writer"
    CRITIC = "critic"
