from typing import Optional

import typer
from rich import print_json

from agentex.cli.handlers.agent_handlers import run_agent_action_server, create_agent, get_agent, list_agents, \
    delete_agent
from agentex.client.agentex import Agentex
from agentex.utils.logging import make_logger

logger = make_logger(__name__)

agents = typer.Typer()


# @agents.command()
# def serve(
#     manifest: Optional[str] = typer.Option(
#         None, help="Path to the manifest you want to use"
#     ),
#     host_port: Optional[int] = typer.Option(
#         8000,
#         help="Port on the host to forward to from the container. If not provided, a random free port will be used."
#     ),
#     container_port: Optional[int] = typer.Option(
#         8000,
#         help="Port on the container to forward to the host. This should be the port at which your uvicorn server is "
#              "running as specified in your Dockerfile."
#     )
# ):
#     """
#     Run the agent's action server with the given manifest path.
#     """
#     logger.info(f"Running agent action server with manifest: {manifest}")
#     run_agent_action_server(manifest_path=manifest, host_port=host_port, container_port=container_port)


@agents.command()
def create(
    manifest: Optional[str] = typer.Option(
        None, help="Path to the manifest you want to use"
    )
):
    """
    Register an action with the given manifest path.
    """
    typer.echo(f"Registering action with manifest: {manifest}")
    client = Agentex()
    agent = create_agent(client, manifest)
    logger.info(f"Agent created: {agent}")


@agents.command()
def get(
    agent_id: str = typer.Argument(
        ...,
        help="ID of the agent to get"
    ),
):
    """
    Get the agent with the given name.
    """
    logger.info(f"Getting agent with ID: {agent_id}")
    client = Agentex()
    agent = get_agent(agentex=client, agent_id=agent_id)
    logger.info(f"Agent retrieved: {agent}")
    print_json(data=agent.to_dict())


@agents.command()
def list():
    """
    List all agents.
    """
    logger.info("Listing all agents")
    client = Agentex()
    agents = list_agents(agentex=client)
    logger.info(f"Agents retrieved: {agents}")
    print_json(data=[agent.to_dict() for agent in agents])


@agents.command()
def delete(
    agent_name: str = typer.Argument(
        ...,
        help="Name of the agent to delete"
    ),
):
    """
    Delete the agent with the given name.
    """
    logger.info(f"Deleting agent with name: {agent_name}")
    client = Agentex()
    delete_agent(agentex=client, agent_name=agent_name)
    logger.info(f"Agent deleted: {agent_name}")
