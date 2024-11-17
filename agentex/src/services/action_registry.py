import inspect
from enum import Enum
from typing import Callable, Dict, Any, Optional, List, Type

from pydantic import create_model, BaseModel as PydanticBaseModel
from pydantic.fields import FieldInfo

from agentex.exceptions import ClientError
from agentex.src.entities.actions import FunctionCallSchema, FunctionSchema
from agentex.utils.json_schema import resolve_refs
from agentex.utils.model_utils import BaseModel
from agentex.utils.regex import snake_to_title, camel_to_snake


def get_function_params_and_annotations(func):
    signature = inspect.signature(func)
    params = signature.parameters
    annotations = {}
    if '_reserved' not in params:
        raise ClientError(
            f"Function '{func.__name__}' must define a '_reserved' parameter to store reserved variable values."
            f"If unused, set it to Optional and None. Ex. _reserved: Optional[Dict[str, Any]] = None"
        )
    for name, param in params.items():
        if name == 'self' or name == '_reserved':
            continue
        if param.annotation == inspect.Parameter.empty:
            raise ClientError(f"The parameter '{name}' in '{func.__name__}' lacks a type annotation.")
        if isinstance(param.default, FieldInfo):
            if not param.default.description:
                raise ClientError(
                    f"Parameter '{name}' in '{func.__name__}' must be set to a pydantic Field with a "
                    f"'description'. Ex. arg = Field(..., description='arg description')"
                )
            default = param.default
        elif param.default != inspect.Parameter.empty:
            default = param.default
        else:
            default = ...
        annotations[name] = (param.annotation, default)
    return annotations


def create_pydantic_model_from_annotations(model_name, annotations):
    return create_model(model_name, **annotations)


class ActionRegistryEntry(BaseModel):
    fn: Callable
    args_model: Type[PydanticBaseModel]
    function_call_schema: FunctionCallSchema


class ReservedKey(str, Enum):
    TASK_ID = "task_id"


class ActionRegistry:
    def __init__(self):
        self.registry: Dict[str, ActionRegistryEntry] = {}
        # Collect action entries from methods
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_action_entry'):
                key, entry = attr._action_entry  # noqa
                # Since attr is already bound to self, we can use it directly
                entry.fn = attr
                self.registry[key] = entry

    async def call(self, name: str, params: Dict[str, Any]) -> Any:
        action_entry = self.registry[name]
        validated_params = action_entry.args_model(**params)

        # Pass the Pydantic model's attributes without serializing them to a dict
        result = action_entry.fn(
            _reserved=params.get("_reserved"),
            **{field: getattr(validated_params, field) for field in validated_params.__fields__}
        )

        if inspect.isawaitable(result):
            result = await result
        return result

    def get_function_call_schema_list(self) -> List[FunctionCallSchema]:
        return [entry.function_call_schema for entry in self.registry.values()]


def action(description: str, name: Optional[str] = None) -> Callable:
    def decorator(action_fn: Callable) -> Callable:
        key = name or action_fn.__name__
        # Extract annotations and create Pydantic model
        annotations = get_function_params_and_annotations(action_fn)
        args_model = create_pydantic_model_from_annotations(
            model_name=f"{snake_to_title(action_fn.__name__)}Params",
            annotations=annotations
        )
        # Build the ActionRegistryEntry
        entry = ActionRegistryEntry(
            fn=action_fn,  # We'll set this later
            args_model=args_model,
            function_call_schema=FunctionCallSchema(
                type="function",
                function=FunctionSchema(
                    name=camel_to_snake(action_fn.__name__),
                    description=description.strip(),
                    parameters=resolve_refs(args_model.schema())
                )
            ))
        # Attach the entry to the function
        action_fn._action_entry = (key, entry)
        return action_fn  # Return the original function

    return decorator

# class HelloWorldActions(ActionRegistry):
#     @action(description="Says hello to the name provided.")
#     async def say_hello(
#         self,
#         name: str = Field(..., description="The name to say hello to.")
#     ) -> ActionResponse:
#         return ActionResponse(message=f"Hello, {name}!")
#
#
# actions = HelloWorldActions()
# print(actions.registry)
