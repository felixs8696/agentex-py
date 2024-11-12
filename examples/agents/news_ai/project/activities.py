from typing import List

from GoogleNews import GoogleNews

from agentex.src.entities.actions import Action, ActionResponse, Artifact
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
{'\n\n'.join([str(article.to_dict()) for article in articles])},
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
                            "link": remove_query_params(article.link),
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


class ReportTerminalFailure(Action):
    """
    Report a terminal failure in the workflow.
    """
    message: str

    async def execute(self) -> ActionResponse:
        return ActionResponse(
            message=self.message,
        )
