from typing import List

from GoogleNews import GoogleNews
from pydantic import BaseModel, Field

# Importing hypothetical AgentEX SDK components
# Ensure that agentex-sdk is installed and accessible
from agentex.src.entities.actions import Artifact, ActionResponse, Action
from agentex.sdk.agent import Agent


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


# Define the Agent

agent = Agent(
    name="DynamicAITechNewsTracker",
    description="An AI agent that dynamically discovers and tracks the hottest AI tech companies and news without hardcoding.",
    model="gpt-4o-mini",
    version="0.0.3",
    instructions=(
        "You are an AI agent designed to fetch and summarize the latest AI technology news. "
        "Your tasks include fetching news articles, processing provided company data, "
        "and compiling a summarized document suitable for a CEO of a budding startup."
    ),
)


# Action to Fetch News
@agent.action(test_payload={"keyword": "AI", "language": "en", "period": "7d"})
class FetchNewsAction(Action):
    """
    Fetch the latest news articles related to AI using GoogleNews.
    """
    keyword: str = Field(
        ...,
        description="The keyword to search for in news articles."
    )
    language: str = Field(
        "en",
        description="The language of the news articles."
    )
    period: str = Field(
        "7d",
        description="The time period for fetching news (e.g., '1d', '7d', '30d')."
    )

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


# Action to Process News with Provided Companies
@agent.action(test_payload={"fetched_articles": [], "provided_companies": []})
class ProcessNewsAction(Action):
    """
    Process fetched news articles to filter relevant articles based on provided companies.
    """
    fetched_articles: List[NewsArticle] = Field(
        ...,
        description="List of fetched news articles to process."
    )
    provided_companies: List[Company] = Field(
        ...,
        description="List of provided and categorized companies."
    )

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


# Action to Write Summary Document
@agent.action(test_payload={"name": "AI_Tech_News_Summary", "description": "Summary of latest AI tech news.",
                            "markdown_content": "# Sample"})
class WriteSummaryAction(Action):
    """
    Write a summarized document of relevant news articles.
    """
    name: str = Field(
        ...,
        description="The name of the summary document to write."
    )
    description: str = Field(
        ...,
        description="A short description of the summary document."
    )
    markdown_content: str = Field(
        ...,
        description="The markdown content of the summary document."
    )

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
