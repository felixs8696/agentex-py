from typing import Annotated

import typer
from rich import print_json

from agentex.cli.handlers.task_handlers import submit_task, modify_task, get_task, list_tasks, delete_task
from agentex.client.agentex import Agentex
from agentex.client.types.tasks import InstructTaskRequest, ApproveTaskRequest, \
    CancelTaskRequest
from agentex.utils.logging import make_logger

logger = make_logger(__name__)

tasks = typer.Typer()


@tasks.command()
def submit(
    agent: str = typer.Option(
        None, help="Name of the agent you want to submit the task to"
    ),
    task: str = typer.Option(
        None, help="Prompt for the task"
    ),
    require_approval: Annotated[
        bool,
        typer.Option(
            "--require-approval",
            "-r/-R",
            help="Whether the task requires human approval in order to complete. "
                 "If false, the task is left running until the human sends an approve message"
        )
    ] = False,
):
    """
    Submit a task to the given agent.
    """
    logger.info(f"Submitting task to agent: {agent}")
    client = Agentex()
    task = submit_task(
        agentex=client,
        agent_name=agent,
        task=task,
        require_approval=require_approval,
    )
    logger.info(f"Task submitted: {task.id}")
    print_json(data=task.to_dict())


@tasks.command()
def get(
    task_id: str = typer.Argument(
        ...,
        help="ID of the task to get"
    ),
):
    """
    Get the task with the given ID.
    """
    logger.info(f"Getting task: {task_id}")
    client = Agentex()
    task = get_task(agentex=client, task_id=task_id)
    print(f"Full Task {task_id}:")
    print_json(data=task.to_dict())


@tasks.command()
def list():
    """
    List all tasks.
    """
    client = Agentex()
    tasks = list_tasks(agentex=client)
    print_json(data=[task.to_dict() for task in tasks])


@tasks.command()
def delete(
    task_id: str = typer.Argument(
        ...,
        help="ID of the task to delete"
    ),
):
    """
    Delete the task with the given ID.
    """
    logger.info(f"Deleting task: {task_id}")
    client = Agentex()
    delete_task(agentex=client, task_id=task_id)
    logger.info(f"Task deleted: {task_id}")


@tasks.command()
def tail(
    task_id: str = typer.Argument(
        ...,
        help="ID of the task to get"
    ),
):
    """
    Get the task with the given ID.
    """
    logger.info(f"Getting task: {task_id}")
    client = Agentex()
    task = get_task(agentex=client, task_id=task_id)
    # print(f"Last Response {task_id}:")
    logger.info(f"Agentex ({task_id}): {task.messages[-1].content}")


@tasks.command()
def instruct(
    task_id: str = typer.Argument(
        ...,
        help="ID of the task to add your instruction to"
    ),
    instruction: str = typer.Argument(
        ...,
        help="Instruction to send to the task"
    ),
):
    """
    Instruct a task with the given instruction.
    """
    client = Agentex()
    modify_task(
        agentex=client,
        task_id=task_id,
        request=InstructTaskRequest(prompt=instruction)
    )
    logger.info(f"Instructing task: {task_id}")


@tasks.command()
def approve(
    task_id: str = typer.Argument(
        ...,
        help="ID of the task to approve"
    ),
):
    """
    Approve a task.
    """
    client = Agentex()
    modify_task(
        agentex=client,
        task_id=task_id,
        request=ApproveTaskRequest()
    )
    logger.info(f"Approving task: {task_id}")


@tasks.command()
def cancel(
    task_id: str = typer.Argument(
        ...,
        help="ID of the task to cancel"
    ),
):
    """
    Cancel a task.
    """
    client = Agentex()
    modify_task(
        agentex=client,
        task_id=task_id,
        request=CancelTaskRequest()
    )
    logger.info(f"Cancelling task: {task_id}")
