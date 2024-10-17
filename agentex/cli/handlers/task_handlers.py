from rich.console import Console

from agentex.client.agentex import Agentex
from agentex.utils.logging import make_logger

logger = make_logger(__name__)
console = Console()


def submit_task(agentex: Agentex, agent_name: str, agent_version: str, task: str):

    return agentex.tasks.create(
        agent_name=agent_name,
        agent_version=agent_version,
        prompt=task,
    )
