import dataclasses
import datetime
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, Type, Union, Callable
from typing import List

from aiohttp import web
from temporalio.client import Client
from temporalio.converter import (
    AdvancedJSONEncoder,
    CompositePayloadConverter,
    DataConverter,
    DefaultPayloadConverter,
    JSONPlainPayloadConverter,
    JSONTypeConverter,
    _JSONTypeConverterUnhandled,
)
from temporalio.runtime import OpenTelemetryConfig, Runtime, TelemetryConfig
from temporalio.worker import UnsandboxedWorkflowRunner, Worker

from agentex.utils.logging import make_logger

logger = make_logger(__name__)


class DateTimeJSONEncoder(AdvancedJSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super().default(o)


class DateTimeJSONTypeConverter(JSONTypeConverter):
    def to_typed_value(
        self, hint: Type, value: Any
    ) -> Union[Optional[Any], _JSONTypeConverterUnhandled]:
        if hint == datetime.datetime:
            return datetime.datetime.fromisoformat(value)
        return JSONTypeConverter.Unhandled


class DateTimePayloadConverter(CompositePayloadConverter):
    def __init__(self) -> None:
        json_converter = JSONPlainPayloadConverter(
            encoder=DateTimeJSONEncoder,
            custom_type_converters=[DateTimeJSONTypeConverter()],
        )
        super().__init__(
            *[
                c if not isinstance(c, JSONPlainPayloadConverter) else json_converter
                for c in DefaultPayloadConverter.default_encoding_payload_converters
            ]
        )


custom_data_converter = dataclasses.replace(
    DataConverter.default,
    payload_converter_class=DateTimePayloadConverter,
)


async def get_temporal_client(temporal_address: str, metrics_url: str = None) -> Client:
    if not metrics_url:
        client = await Client.connect(
            target_host=temporal_address, data_converter=custom_data_converter
        )
    else:
        runtime = Runtime(telemetry=TelemetryConfig(metrics=OpenTelemetryConfig(url=metrics_url)))
        client = await Client.connect(
            target_host=temporal_address, data_converter=custom_data_converter, runtime=runtime
        )
    return client


class AgentexWorker:

    def __init__(
        self,
        task_queue,
        max_workers: int = 10,
        max_concurrent_activities: int = 10
    ):
        self.task_queue = task_queue
        self.activity_handles = []
        self.max_workers = max_workers
        self.max_concurrent_activities = max_concurrent_activities
        self.health_check_server_running = False
        self.healthy = False

    async def run(
        self,
        activities: List[Callable],
        workflow: Type,
    ):
        await self.start_health_check_server()
        try:
            temporal_client = await get_temporal_client(
                temporal_address=os.environ.get("TEMPORAL_ADDRESS"),
            )
            worker = Worker(
                client=temporal_client,
                task_queue=self.task_queue,
                activity_executor=ThreadPoolExecutor(max_workers=self.max_workers),
                workflows=[workflow],
                activities=activities,
                workflow_runner=UnsandboxedWorkflowRunner(),
                max_concurrent_activities=self.max_concurrent_activities,
                build_id=str(uuid.uuid4()),
            )

            logger.info(f"Starting workers for task queue: {self.task_queue}")
            # Eagerly set the worker status to healthy
            self.healthy = True
            logger.info(f"Running workers for task queue: {self.task_queue}")
            await worker.run()

        except Exception as e:
            logger.error(f"Agent task worker encountered an error: {e}")
            self.healthy = False

    async def _health_check(self):
        return web.json_response(self.healthy)

    async def start_health_check_server(self):
        if not self.health_check_server_running:
            app = web.Application()
            app.router.add_get('/readyz', lambda request: self._health_check())

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 80)  # Expose on port 80
            await site.start()
            logger.info("Health check server running on http://0.0.0.0:80/readyz")
            self.health_check_server_running = True
