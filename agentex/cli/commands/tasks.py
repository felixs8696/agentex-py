import typer

from agentex.cli.handlers.task_handlers import submit_task
from agentex.client.agentex import Agentex
from agentex.utils.logging import make_logger

logger = make_logger(__name__)

tasks = typer.Typer()


@tasks.command()
def submit(
    agent: str = typer.Option(
        None, help="Name of the agent you want to submit the task to"
    ),
    version: str = typer.Option(
        None, help="Version of the agent you want to submit the task to"
    ),
    task: str = typer.Option(
        None, help="Prompt for the task"
    ),
):
    """
    Submit a task to the given agent.
    """
    logger.info(f"Submitting task to agent: {agent}")
    client = Agentex()
    submit_task(agentex=client, agent_name=agent, agent_version=version, task=task)
