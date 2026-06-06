from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import SessionLocal
from app.models.visitor import Visitor
from app.services.visitor_service import is_temporary_avatar_url


def clear_temporary_visitor_avatars() -> int:
    db = SessionLocal()
    try:
        visitors = [visitor for visitor in db.query(Visitor).all() if is_temporary_avatar_url(visitor.avatar_url)]
        for visitor in visitors:
            visitor.avatar_url = None
        db.commit()
        return len(visitors)
    finally:
        db.close()


if __name__ == "__main__":
    cleared = clear_temporary_visitor_avatars()
    print(f"cleared_temporary_visitor_avatars={cleared}")
