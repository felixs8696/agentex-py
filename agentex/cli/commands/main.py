import asyncio

import typer

from agentex.cli.commands.agents import agents
from agentex.client.agentex import AsyncAgentex

# Create the main Typer application
app = typer.Typer(
    context_settings=dict(help_option_names=["-h", "--help"], max_content_width=800),
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
    add_completion=False,
)

# Add the 'actions' subcommand from the imported module
app.add_typer(agents, name="agent")


async def async_hello():
    agentex = AsyncAgentex()
    response = await agentex.get("/")
    typer.echo(response.text)


@app.command()
def hello():
    asyncio.run(async_hello())


if __name__ == "__main__":
    app()
