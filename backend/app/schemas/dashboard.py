from datetime import datetime

from pydantic import BaseModel


class DashboardOverview(BaseModel):
    total_events: int
    total_spots: int
    total_documents: int
    recent_import_jobs: list


class FeedbackDetail(BaseModel):
    id: int
    message_id: int | None
    session_id: int | None
    sentiment: str | None
    score: float | None
    content: str | None
    question_text: str | None
    answer_text: str | None
    created_at: datetime


class FeedbackTrendItem(BaseModel):
    date: str
    total_feedback: int
    average_score: float | None
    negative_count: int


class FeedbackTopItem(BaseModel):
    name: str
    count: int


class NegativeReasonItem(BaseModel):
    reason: str
    count: int


class RouteFeedbackAnalysisItem(BaseModel):
    route_name: str
    total_feedback: int
    average_score: float | None
    negative_count: int


class FeedbackReport(BaseModel):
    total_feedback: int
    average_score: float | None
    sentiment_distribution: dict[str, int]
    suggestion_summary: str
    latest_feedback: list[FeedbackDetail]
    feedback_trend: list[FeedbackTrendItem] = []
    focus_top_n: list[FeedbackTopItem] = []
    complaint_top_n: list[FeedbackTopItem] = []
    negative_reason_top_n: list[NegativeReasonItem] = []
    route_feedback_analysis: list[RouteFeedbackAnalysisItem] = []
