from pydantic import BaseModel


class DashboardOverview(BaseModel):
    total_events: int
    total_spots: int
    total_documents: int
    recent_import_jobs: list


class FeedbackReport(BaseModel):
    total_feedback: int
    average_score: float | None
    sentiment_distribution: dict[str, int]
    suggestion_summary: str
