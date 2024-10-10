import json
from typing import Optional
from pathlib import Path

from rich.console import Console
from python_on_whales import docker

from agentex.client.agentex import Agentex
from agentex.client.types.agents import CreateAgentRequest
from agentex.sdk.agent import Agent
from agentex.utils.console import print_section
from agentex.utils.logging import make_logger
from agentex.cli.models.action_manifest import ActionManifestConfig

logger = make_logger(__name__)
console = Console()


def run_agent_action_server(manifest_path: str, host_port: Optional[int] = None, container_port: Optional[int] = None):
    action_manifest = ActionManifestConfig.from_yaml(file_path=manifest_path)
    build_context_root = (Path(manifest_path).parent / action_manifest.build.context.root).resolve()
    with action_manifest.context_manager(build_context_root) as build_context:
        # Use the build_context_root directly as the context for Docker
        image = f'{action_manifest.build.image.repository}:{action_manifest.build.image.tag}'
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
    action_manifest = ActionManifestConfig.from_yaml(file_path=manifest_path)
    build_context_root = (Path(manifest_path).parent / action_manifest.build.context.root).resolve()
    with action_manifest.context_manager(build_context_root) as build_context:
        with build_context.zipped(build_context.path) as zip_stream:
            params = CreateAgentRequest(
                agent_package=('context.tar.gz', zip_stream, 'application/gzip'),
                name=action_manifest.name,
                description=action_manifest.description,
                parameters=json.dumps({
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the caller",
                        },
                    },
                    "required": ["name"],
                }),
                test_payload=json.dumps(action_manifest.test_payload),
                version=action_manifest.version,
                agents=json.dumps([]),
            )

            logger.info(f"Creating action with payload: {params}")

            return agentex.actions.create(**params)

