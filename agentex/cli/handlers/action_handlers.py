import json
from pathlib import Path

from agentex import Agentex
from agentex.types import ActionCreateParams
from agentex.utils.logging import make_logger
from agentex.cli.models.action_manifest import ActionManifestConfig

logger = make_logger(__name__)


def create_action(agentex: Agentex, manifest_path: str):
    action_manifest = ActionManifestConfig.from_yaml(file_path=manifest_path)
    build_context_root = (Path(manifest_path).parent / action_manifest.build.context.root).resolve()
    with action_manifest.context_manager(build_context_root) as build_context:
        with build_context.zipped(build_context.path) as zip_stream:
            params = ActionCreateParams(
                code_package=('context.tar.gz', zip_stream, 'application/gzip'),
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
