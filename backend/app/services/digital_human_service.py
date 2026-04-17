from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.settings_repo import SettingsRepository
from app.schemas.digital_human import DigitalHumanCreate, DigitalHumanUpdate


class DigitalHumanService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SettingsRepository(db)

    def list_all(self):
        return self.repo.list_digital_humans()

    def create(self, payload: DigitalHumanCreate):
        return self.repo.create_digital_human(**payload.model_dump())

    def update(self, config_id: int, payload: DigitalHumanUpdate):
        item = self.repo.get_digital_human(config_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Digital human config not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item
