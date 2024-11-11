from pathlib import Path
from typing import Optional

from python_on_whales import docker
from rich.console import Console

from agentex.cli.models.action_manifest import AgentManifestConfig
from agentex.client.agentex import Agentex
from agentex.client.types.agents import CreateAgentRequest
from agentex.utils.console import print_section
from agentex.utils.logging import make_logger

logger = make_logger(__name__)
console = Console()


def run_agent_action_server(manifest_path: str, host_port: Optional[int] = None, container_port: Optional[int] = None):
    agent_manifest = AgentManifestConfig.from_yaml(file_path=manifest_path)
    build_context_root = (Path(manifest_path).parent / agent_manifest.build.context.root).resolve()
    with agent_manifest.context_manager(build_context_root) as build_context:
        # Use the build_context_root directly as the context for Docker
        image = f'{agent_manifest.build.image.repository}:{agent_manifest.build.image.tag}'
        build_logs = docker.build(
            context_path=str(build_context.path),  # Use the build context folder
            tags=image,
            stream_logs=True,
            cache=True,
        )

        print_section(name="Building Image", contents=["Image", image])

        with console.status(f"[bold green]Building image: {image}...") as status:
            for line in build_logs:
                console.log(line.strip())

        # Run the container from the built image
        print_section(
            name=f"Running Container",
            subtitle=f"View docs at localhost:{host_port}/docs",
            contents=["Image", image]
        )
        if container_port:
            if host_port:
                port_mapping = [(f"{host_port}", f"{container_port}")]
            else:
                port_mapping = [(f"{container_port}",)]
        else:
            port_mapping = ()

        output_generator = docker.run(image=image, stream=True, publish=port_mapping)
        with console.status(f"[bold green]Running container for {image}. (Ctrl+C to stop)...") as status:
            for _, stream_content in output_generator:
                console.log(stream_content.decode().strip())


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
