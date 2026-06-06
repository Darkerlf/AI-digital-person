from typing import Any

from sqlalchemy.orm import Session

from app.repositories.operation_log_repo import OperationLogRepository


def _user_id(current_user: Any | None) -> int | None:
    return getattr(current_user, "id", None) if current_user is not None else None


def record_operation_log(
    db: Session,
    *,
    module: str,
    action: str,
    target_type: str | None = None,
    target_id: int | None = None,
    detail: dict[str, Any] | None = None,
    current_user: Any | None = None,
):
    return OperationLogRepository(db).create(
        admin_user_id=_user_id(current_user),
        module=module,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail_json=detail or {},
    )
