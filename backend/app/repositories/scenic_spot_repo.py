from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.scenic_spot import ScenicSpot
from app.models.scenic_spot_tag import ScenicSpotTag


class ScenicSpotRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self, keyword: str | None = None, open_status: str | None = None) -> list[ScenicSpot]:
        statement = select(ScenicSpot)
        if keyword:
            pattern = f"%{keyword}%"
            statement = statement.where(
                or_(
                    ScenicSpot.name.like(pattern),
                    ScenicSpot.alias.like(pattern),
                    ScenicSpot.spot_code.like(pattern),
                )
            )
        if open_status:
            statement = statement.where(ScenicSpot.open_status == open_status)
        return self.db.execute(statement.order_by(ScenicSpot.id.asc())).scalars().all()

    def get(self, spot_id: int) -> ScenicSpot | None:
        return self.db.get(ScenicSpot, spot_id)

    def create(self, **kwargs) -> ScenicSpot:
        tags = kwargs.pop("tags", [])
        spot = ScenicSpot(**kwargs)
        self.db.add(spot)
        self.db.flush()
        for tag_name in tags:
            self.db.add(ScenicSpotTag(scenic_spot_id=spot.id, tag_name=tag_name))
        self.db.commit()
        self.db.refresh(spot)
        return spot
