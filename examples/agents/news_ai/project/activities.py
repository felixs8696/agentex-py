from typing import List, Any, Dict, Optional

from GoogleNews import GoogleNews
from pydantic import Field

from agentex.src.entities.actions import ActionResponse, Artifact
from agentex.src.services.action_registry import ActionRegistry, action
from agentex.utils.model_utils import BaseModel
from agentex.utils.parsing import remove_query_params


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


class NewsActions(ActionRegistry):

    @action(description="Fetch the latest news articles related to a given topic using GoogleNews.")
    async def fetch_news(
        self,
        keyword: str = Field(..., description="The keyword to search news for."),
        language: str = Field(default="en", description="Language of the news articles."),
        period: str = Field(default="7d", description="Time period for news search."),
        _reserved: Optional[Dict[str, Any]] = None,
    ) -> ActionResponse:
        try:
            gn = GoogleNews(lang=language, period=period)
            gn.search(keyword)
            results = gn.result()
            articles = [NewsArticle(**article) for article in results]
            return ActionResponse(
                message=f"Fetched {len(articles)} articles related to '{keyword}':\n"
                        f"{', '.join([article.title for article in articles])}",
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to fetch news articles: {str(e)}",
                success=False
            )

    @action(description="Process fetched news articles and filter relevant ones based on company data.")
    async def process_news(
        self,
        fetched_articles: List[NewsArticle] = Field(..., description="List of fetched news articles."),
        provided_companies: List[Company] = Field(..., description="List of companies to filter articles by."),
        _reserved: Optional[Dict[str, Any]] = None,
    ) -> ActionResponse:
        try:
            relevant_articles = []
            company_names = [company.name for company in provided_companies]

            for article in fetched_articles:
                for company in company_names:
                    if company.lower() in article.title.lower() or company.lower() in article.desc.lower():
                        relevant_articles.append({
                            "company": company,
                            "category": next((c.category for c in provided_companies if c.name == company), "Other"),
                            "title": article.title,
                            "description": article.desc,
                            "link": remove_query_params(article.link),
                            "date": article.date,
                            "media": article.media
                        })
                        break

            return ActionResponse(
                message=f"Processed articles. Found {len(relevant_articles)} relevant articles:\n"
                        f"{', '.join([article['title'] for article in relevant_articles])}",
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to process news articles: {str(e)}",
            )

    @action(description="Write a summary document based on the provided markdown.")
    async def write_summary(
        self,
        name: str = Field(..., description="The name of the summary document."),
        description: str = Field(..., description="Description of the summary."),
        markdown_content: str = Field(..., description="The markdown content to save."),
        _reserved: Optional[Dict[str, Any]] = None,
    ) -> ActionResponse:
        try:
            filename = f"{name.replace(' ', '_')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            return ActionResponse(
                message=f"Summary document '{filename}' written successfully.",
                artifacts=[
                    Artifact(
                        name=name,
                        description=description,
                        content=markdown_content
                    )
                ]
            )
        except Exception as e:
            return ActionResponse(
                message=f"Failed to write summary document: {str(e)}",
            )

    @action(description="Report a terminal failure in the workflow.")
    async def report_terminal_failure(
        self,
        message: str = Field(..., description="Failure message to report."),
        _reserved: Optional[Dict[str, Any]] = None,
    ) -> ActionResponse:
        return ActionResponse(
            message=message,
        )
