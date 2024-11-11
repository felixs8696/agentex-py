from datetime import timedelta
from typing import Union, Optional, Type, List, TypeVar, get_origin, get_args, Dict, Tuple

from temporalio import workflow
from temporalio.common import RetryPolicy

from agentex.utils.model_utils import BaseModel

T = TypeVar("T", bound="BaseModel")


class WorkflowHelper:

    @staticmethod
    async def execute_activity(
        activity_name: str,
        arg: Union[BaseModel, str, int, float, bool, dict, list],
        start_to_close_timeout: Optional[timedelta],
        retry_policy: Optional[RetryPolicy] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[List, Dict, Tuple, T]:
        if start_to_close_timeout is None:
            start_to_close_timeout = timedelta(seconds=10)
        if retry_policy is None:
            retry_policy = RetryPolicy(maximum_attempts=0)

        response = await workflow.execute_activity(
            activity=activity_name,
            arg=arg,
            start_to_close_timeout=start_to_close_timeout,
            retry_policy=retry_policy,
        )

        if response_model:
            origin = get_origin(response_model)
            args = get_args(response_model)

            if origin in [list, List]:  # Handles List[T]
                return [args[0].from_dict(item) if isinstance(item, dict) else item for item in response]

            elif origin in [Optional, Union] and args:  # Handles Optional[T] or Union[T, None]
                actual_type = args[0] if args[0] is not type(None) else args[1]
                if isinstance(response, dict) and issubclass(actual_type, BaseModel):
                    return actual_type.from_dict(response)
                return response

            elif origin in [dict, Dict]:  # Handles Dict
                return {k: v for k, v in response.items()}

            elif origin in [tuple, Tuple]:  # Handles Tuple
                return tuple(response)

            elif issubclass(response_model, BaseModel):  # Handles BaseModel directly
                if isinstance(response, dict):
                    return response_model.from_dict(response)

        return response
