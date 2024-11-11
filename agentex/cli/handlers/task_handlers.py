from typing import Optional

from rich.console import Console

from agentex.client.agentex import Agentex
from agentex.client.types.tasks import ModifyTaskRequest
from agentex.utils.logging import make_logger

logger = make_logger(__name__)
console = Console()


def submit_task(
    agentex: Agentex,
    agent_name: str,
    task: str,
    require_approval: Optional[bool] = False
):
    return agentex.tasks.create(
        agent_name=agent_name,
        prompt=task,
        require_approval=require_approval,
    )


def get_task(agentex: Agentex, task_id: str):
    return agentex.tasks.get(task_id=task_id)


def list_tasks(agentex: Agentex):
    return agentex.tasks.list()


def delete_task(agentex: Agentex, task_id: str):
    return agentex.tasks.delete(task_id=task_id)


def modify_task(agentex: Agentex, task_id: str, request: ModifyTaskRequest):
    return agentex.tasks.modify(task_id=task_id, modification_request=request)
