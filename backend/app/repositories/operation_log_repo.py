from sqlalchemy.orm import Session

from app.models.operation_log import OperationLog


class OperationLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, **kwargs) -> OperationLog:
        log = OperationLog(**kwargs)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
