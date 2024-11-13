from datetime import timedelta
from typing import Union, Optional, Type, List, TypeVar, get_origin, get_args, Dict, Tuple, Any

from pydantic import TypeAdapter
from temporalio import workflow
from temporalio.common import RetryPolicy

from agentex.utils.model_utils import BaseModel

T = TypeVar("T", bound="BaseModel")


class WorkflowHelper:

    @staticmethod
    async def execute_activity(
        activity_name: str,
        request: Union[BaseModel, str, int, float, bool, dict, list],
        response_type: Any,
        start_to_close_timeout: Optional[timedelta],
        retry_policy: Optional[RetryPolicy] = None,
    ) -> Any:
        if start_to_close_timeout is None:
            start_to_close_timeout = timedelta(seconds=10)
        if retry_policy is None:
            retry_policy = RetryPolicy(maximum_attempts=0)

        response = await workflow.execute_activity(
            activity=activity_name,
            arg=request,
            start_to_close_timeout=start_to_close_timeout,
            retry_policy=retry_policy,
        )

        adapter = TypeAdapter(response_type)
        return adapter.validate_python(response)
