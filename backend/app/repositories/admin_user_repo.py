from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin_user import AdminUser


class AdminUserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> AdminUser | None:
        return self.db.execute(select(AdminUser).where(AdminUser.username == username)).scalar_one_or_none()
