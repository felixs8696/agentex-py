from functools import wraps
from typing import Any, Type, Dict, Optional

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agentex.utils.json_schema import resolve_refs
from agentex.utils.logging import make_logger
from agentex.utils.regex import camel_to_snake

logger = make_logger(__name__)


class Agent:

    def __init__(
        self,
        name: str,
        description: str,
        version: str,
        instructions: str,
        model: str = 'gpt-4o-mini',
    ):
        self.name = name
        self.description = description
        self.version = version
        self.instructions = instructions
        self.model = model
        self.actions = []
        self.app = FastAPI(
            title=name,
            summary=description,
            version=version,
        )  # Each agent has its own FastAPI app
        self._set_error_handlers()

    def action(self, test_payload: Optional[Dict] = None) -> Any:
        def decorated(model_cls: Type[BaseModel]):
            # Handle if it's a Pydantic model (class-based)
            assert isinstance(model_cls, type) and issubclass(model_cls, BaseModel)
            # Generate OpenAI schema based on Pydantic model
            action_schema = {
                "name": camel_to_snake(model_cls.__name__),
                "description": model_cls.__doc__.strip(),
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
            self.actions.append(dict(
                schema=action_schema,
                test_payload=test_payload,
            ))
            self._register_fastapi_route(name=action_name, model=model_cls)
            self._update_fastapi_root_route()

            return model_cls
        return decorated

    def serve(self, host: str = '0.0.0.0', port: int = 8000):
        uvicorn.run(self.app, host=host, port=port)

    def _register_fastapi_route(self, name: str, model: Type[BaseModel]):
        """Register a FastAPI route for the action in the agent-specific FastAPI app."""

        @self.app.post(f"/{name}")
        async def handler(request: model):
            return await request.execute()

    def _update_fastapi_root_route(self):

        @self.app.get("/")
        async def root():
            return {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "instructions": self.instructions,
                "model": self.model,
                "actions": self.actions,
            }

        return root

    def _set_error_handlers(self):
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request: Request, exc: RequestValidationError):
            exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
            logger.info(f'Validation error: {exc_str}')
            content = {'status_code': 10422, 'message': exc_str, 'data': None}
            return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
