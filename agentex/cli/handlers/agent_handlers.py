from pathlib import Path

from rich.console import Console

from agentex.cli.models.action_manifest import AgentManifestConfig
from agentex.client.agentex import Agentex
from agentex.client.types.agents import CreateAgentRequest
from agentex.utils.logging import make_logger

logger = make_logger(__name__)
console = Console()


def create_agent(agentex: Agentex, manifest_path: str):
    agent_manifest = AgentManifestConfig.from_yaml(file_path=manifest_path)
    build_context_root = (Path(manifest_path).parent / agent_manifest.build.context.root).resolve()
    with agent_manifest.context_manager(build_context_root) as build_context:
        with build_context.zipped(build_context.path) as zip_stream:
            params = dict(
                agent_package=('context.tar.gz', zip_stream, 'application/gzip'),
                request=CreateAgentRequest(
                    name=agent_manifest.agent.name,
                    description=agent_manifest.agent.description,
                    workflow_name=agent_manifest.workflow.name,
                    workflow_queue_name=agent_manifest.workflow.queue_name,
                )
            )

            logger.info(f"Creating agent with payload: {params}")

            return agentex.agents.create(
                agent_package=params['agent_package'],
                request=params['request'],
            )


def get_agent(agentex: Agentex, agent_id: str):
    return agentex.agents.get(agent_id=agent_id)


def list_agents(agentex: Agentex):
    return agentex.agents.list()


def delete_agent(agentex: Agentex, agent_name: str):
    return agentex.agents.delete(agent_name=agent_name)
