from pydantic import BaseModel


class ImportRequest(BaseModel):
    source_path: str


class ImportJobRead(BaseModel):
    id: int
    job_type: str
    source_file_name: str
    source_file_path: str
    status: str
    total_count: int
    success_count: int
    failed_count: int
    error_message: str | None

    model_config = {"from_attributes": True}
