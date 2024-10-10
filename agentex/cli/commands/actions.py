from typing import Optional

import typer

from agentex.client.agentex import Agentex
from agentex.utils.logging import make_logger
from agentex.cli.handlers.action_handlers import create_action

logger = make_logger(__name__)

# Create a Typer instance for the 'actions' subcommand
actions = typer.Typer()


# Define a function for each command, and the command name will match the function name
@actions.command()
def create(
    build_manifest_path: Optional[str] = typer.Option(
        None, help="Path to the build manifest you want to use"
    )
):
    """
    Register an action with the given manifest path.
    """
    typer.echo(f"Registering action with manifest: {build_manifest_path}")
    client = Agentex()
    action = create_action(client, build_manifest_path)
    logger.info(f"Action created: {action}")
