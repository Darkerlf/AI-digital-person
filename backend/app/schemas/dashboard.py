from pydantic import BaseModel


class DashboardOverview(BaseModel):
    total_events: int
    total_spots: int
    total_documents: int
    recent_import_jobs: list
