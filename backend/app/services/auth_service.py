from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.repositories.admin_user_repo import AdminUserRepository


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.admin_users = AdminUserRepository(db)

    def login(self, username: str, password: str) -> str | None:
        user = self.admin_users.get_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            return None
        return create_access_token(user.username)
