from sqlalchemy.orm import Session

from app.repositories.settings_repo import SettingsRepository


class AIAdapterService:
    def __init__(self, db: Session) -> None:
        self.repo = SettingsRepository(db)

    def list_provider_configs(self):
        return self.repo.list_ai_providers()

    def get_active_provider(self, model_type: str):
        return self.repo.get_active_ai_provider(model_type)

    def build_future_client_config(self, model_type: str) -> dict | None:
        provider = self.get_active_provider(model_type)
        if provider is None:
            return None
        return {
            "provider_name": provider.provider_name,
            "endpoint": provider.endpoint,
            "model_type": provider.model_type,
        }
