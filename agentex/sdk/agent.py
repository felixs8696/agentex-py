from typing import Any, Type
from functools import wraps

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from agentex.utils.regex import camel_to_snake
from agentex.utils.json_schema import resolve_refs


class Agent:

    def __init__(
        self,
        name: str,
        description: str,
        version: str,
        instructions: str,
        model: str = 'gpt-4o-mini',
        fastapi_app: FastAPI = None,
    ):
        self.app = fastapi_app or FastAPI()  # Each agent has its own FastAPI app
        self.name = name
        self.description = description
        self.version = version
        self.instructions = instructions
        self.model = model
        self.actions = {}

    def action(self, model_cls: Type[BaseModel]) -> Any:
        # Handle if it's a Pydantic model (class-based)
        assert isinstance(model_cls, type) and issubclass(model_cls, BaseModel)
        # Generate OpenAI schema based on Pydantic model
        action_schema = {
            "name": model_cls.__name__,
            "description": model_cls.__doc__,
            "parameters": resolve_refs(model_cls.schema()),
        }

        # Modify the class to include `action_schema`
        model_cls.action_schema = {
            "type": "function",
            "function": action_schema,
        }

        # Decorate the `execute` method, if it exists, for validation
        original_execute = model_cls.execute

        @wraps(original_execute)
        def wrapped_execute(self, *args: Any, **kwargs: Any) -> Any:
            return original_execute(self, *args, **kwargs)

        model_cls.execute = wrapped_execute

        action_name = camel_to_snake(model_cls.__name__)
        self.actions[action_name] = model_cls
        self._register_fastapi_route(name=action_name, model=model_cls)

        return model_cls

    def serve(self, host: str = '0.0.0.0', port: int = 8000):
        uvicorn.run(self.app, host=host, port=port)

    def _register_fastapi_route(self, name: str, model: Type[BaseModel]):
        """Register a FastAPI route for the action in the agent-specific FastAPI app."""

        @self.app.post(f"/{name}")
        async def handler(request: model):
            return await request.execute()
