import asyncio
from datetime import timedelta
from typing import List

from GoogleNews import GoogleNews
from temporalio import workflow
from temporalio.common import RetryPolicy

from agentex.client.types.tasks import UserMessage, SystemMessage
from agentex.constants import DEFAULT_ROOT_THREAD_NAME
from agentex.sdk.execution.helpers import WorkflowHelper
from agentex.sdk.execution.workflow import AgentTaskWorkflowParams, AgentStatus, BaseWorkflow
from agentex.sdk.lib.activities.names import ActivityName
from agentex.sdk.lib.activities.state import AppendMessagesToThreadParams
from agentex.sdk.lib.workflows.action_loop import ActionLoop
from agentex.src.entities.actions import Action, ActionResponse, Artifact, ActionRegistry
from agentex.utils.logging import make_logger
from agentex.utils.model_utils import BaseModel

logger = make_logger(__name__)


# Define data models using Pydantic
class NewsArticle(BaseModel):
    title: str
    media: str
    date: str
    desc: str
    link: str


class Company(BaseModel):
    name: str
    mention_count: int
    category: str  # e.g., Startup, Model Provider, Cloud Provider, etc.


class FetchNews(Action):
    """
    Fetch the latest news articles related to a given topic using GoogleNews.
    """

    keyword: str
    language: str = "en"
    period: str = "7d"

    async def execute(self) -> ActionResponse:
        try:
            gn = GoogleNews(lang=self.language, period=self.period)
            gn.search(self.keyword)
            results = gn.result()
            articles = [NewsArticle(**article) for article in results]
            return ActionResponse(
                message=f"""Fetched {len(articles)} articles related to '{self.keyword}':
{'\n\n'.join([str(article.dict()) for article in articles])},
        """,
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to fetch news articles: {str(e)}",
                success=False
            )


class ProcessNews(Action):
    """
    Process the fetched news articles and filter out the relevant ones based on provided company data.
    """
    fetched_articles: List[NewsArticle]
    provided_companies: List[Company]

    async def execute(self) -> ActionResponse:
        try:
            relevant_articles = []
            company_names = [company.name for company in self.provided_companies]

            for article in self.fetched_articles:
                for company in company_names:
                    if company.lower() in article.title.lower() or company.lower() in article.desc.lower():
                        relevant_articles.append({
                            "company": company,
                            "category": next((c.category for c in self.provided_companies if c.name == company),
                                             "Other"),
                            "title": article.title,
                            "description": article.desc,
                            "link": article.link,
                            "date": article.date,
                            "media": article.media
                        })
                        break  # Avoid duplicate entries if multiple companies match

            return ActionResponse(
                message=f"""Processed articles. Found {len(relevant_articles)} relevant articles.
{'\n\n'.join([str(article) for article in relevant_articles])},
""",
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to process news articles: {str(e)}",
            )


class WriteSummary(Action):
    """
    Write a summary document based on the provided markdown
    """
    name: str
    description: str
    markdown_content: str

    async def execute(self) -> ActionResponse:
        try:
            # Save the markdown content to a file.
            filename = f"{self.name.replace(' ', '_')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.markdown_content)
            return ActionResponse(
                message=f"Summary document '{filename}' written successfully.",
                artifacts=[
                    Artifact(
                        name=self.name,
                        description=self.description,
                        content=self.markdown_content
                    )
                ]
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to write summary document: {str(e)}",
            )


@workflow.defn
class NewsAIWorkflow(BaseWorkflow):

    def __init__(self):
        super().__init__()
        self.name = "NewsAI"
        self.description = (
            "An AI agent that dynamically discovers and tracks the hottest AI tech companies and news without "
            "hard-coding."
        )
        self.model = "gpt-4o-mini"
        self.version = "0.0.3"
        self.instructions = (
            "You are an AI agent designed to fetch and summarize the latest AI technology news. "
            "Your tasks include fetching news articles, processing provided company data, "
            "and compiling a summarized document suitable for a CEO of a budding startup."
        )
        self.action_registry = ActionRegistry(actions=[FetchNews, ProcessNews, WriteSummary])

    @workflow.run
    async def run(self, params: AgentTaskWorkflowParams):
        task = params.task
        self.set_status(AgentStatus.ACTIVE)

        try:
            # Give the agent the initial task
            await WorkflowHelper.execute_activity(
                activity_name=ActivityName.APPEND_MESSAGES_TO_THREAD,
                arg=AppendMessagesToThreadParams(
                    task_id=task.id,
                    thread_name=DEFAULT_ROOT_THREAD_NAME,
                    messages=[
                        SystemMessage(content=self.instructions),
                        UserMessage(content=task.prompt)
                    ],
                ),
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )

            # Run the tool loop
            while True:
                logger.info("Running tool loop")
                await ActionLoop.run(
                    task_id=task.id,
                    thread_name=DEFAULT_ROOT_THREAD_NAME,
                    model=self.model,
                    actions=self.action_registry.actions,
                )
                logger.info("Tool loop finished")

                if params.require_approval:
                    logger.info("Waiting for instruction or approval")
                    self.waiting_for_instruction = True
                    logger.info("Waiting for instruction or approval")
                    await workflow.wait_condition(lambda: not self.waiting_for_instruction or self.task_approved)
                    if self.task_approved:
                        logger.info("Task approved")
                        break
                    else:
                        logger.info("Task not approved, but instruction received, so continuing")
                        continue
                else:
                    break
            status = "completed"
        except asyncio.CancelledError as error:
            logger.warning(f"Task canceled by user: {task.id}")
            raise error
        finally:
            # Set the agent status to IDLE
            self.set_status(AgentStatus.IDLE)

        return status
