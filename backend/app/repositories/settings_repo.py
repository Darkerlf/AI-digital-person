from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.admin_user import AdminUser
from app.models.ai_provider_config import AIProviderConfig
from app.models.digital_human_config import DigitalHumanConfig
from app.models.operation_log import OperationLog


class SettingsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_ai_providers(self) -> list[AIProviderConfig]:
        return self.db.execute(select(AIProviderConfig).order_by(AIProviderConfig.id.asc())).scalars().all()

    def get_ai_provider(self, provider_id: int) -> AIProviderConfig | None:
        return self.db.get(AIProviderConfig, provider_id)

    def get_active_ai_provider(self, model_type: str) -> AIProviderConfig | None:
        return self.db.execute(
            select(AIProviderConfig).where(
                AIProviderConfig.model_type == model_type,
                AIProviderConfig.status == "active",
            )
        ).scalar_one_or_none()

    def create_ai_provider(self, **kwargs) -> AIProviderConfig:
        item = AIProviderConfig(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_digital_humans(self) -> list[DigitalHumanConfig]:
        return self.db.execute(select(DigitalHumanConfig).order_by(DigitalHumanConfig.id.asc())).scalars().all()

    def get_digital_human(self, config_id: int) -> DigitalHumanConfig | None:
        return self.db.get(DigitalHumanConfig, config_id)

    def create_digital_human(self, **kwargs) -> DigitalHumanConfig:
        item = DigitalHumanConfig(**kwargs)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_admin_users(self) -> list[AdminUser]:
        return self.db.execute(select(AdminUser).order_by(AdminUser.id.asc())).scalars().all()

    def create_admin_user(self, **kwargs) -> AdminUser:
        user = AdminUser(**kwargs)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_operation_logs(self) -> list[OperationLog]:
        return self.db.execute(select(OperationLog).order_by(OperationLog.id.desc())).scalars().all()
