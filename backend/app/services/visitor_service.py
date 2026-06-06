from datetime import UTC, datetime

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token, JWTError
from app.models.visitor import Visitor


def is_temporary_avatar_url(value: str | None) -> bool:
    avatar_url = (value or "").strip().lower()
    return (
        avatar_url.startswith("wxfile://")
        or avatar_url.startswith("http://tmp/")
        or avatar_url.startswith("https://tmp/")
        or "/__tmp__/" in avatar_url
    )


class VisitorService:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def login_by_wechat(self, code: str, nickname: str | None = None, avatar_url: str | None = None) -> dict:
        # H5 开发模式：使用 mock code 跳过微信 API 调用
        if code.startswith("h5_dev_mock_code_"):
            openid = f"h5_dev_{code}"
            visitor = self.db.query(Visitor).filter(Visitor.openid == openid).first()
            if visitor is None:
                visitor = Visitor(openid=openid)
                self.db.add(visitor)
            if nickname:
                visitor.nickname = nickname
            elif visitor.nickname is None:
                visitor.nickname = "H5测试用户"
            if avatar_url:
                visitor.avatar_url = avatar_url
            visitor.last_login_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(visitor)
            token = create_access_token(f"visitor:{visitor.id}")
            return {
                "token": token,
                "visitor_id": visitor.id,
                "nickname": visitor.nickname or "H5测试用户",
                "avatar_url": visitor.avatar_url or "",
            }

        # 正式微信登录
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": settings.wechat_appid,
            "secret": settings.wechat_secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            data = resp.json()

        openid = data.get("openid")
        if not openid:
            errcode = data.get("errcode", "unknown")
            errmsg = data.get("errmsg", "wx login failed")
            raise ValueError(f"WeChat error {errcode}: {errmsg}")

        session_key = data.get("session_key", "")
        visitor = self.db.query(Visitor).filter(Visitor.openid == openid).first()
        if visitor is None:
            visitor = Visitor(openid=openid, session_key=session_key)
            self.db.add(visitor)
        else:
            visitor.session_key = session_key
        if nickname:
            visitor.nickname = nickname
        if avatar_url:
            visitor.avatar_url = avatar_url
        visitor.last_login_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(visitor)

        token = create_access_token(f"visitor:{visitor.id}")
        return {
            "token": token,
            "visitor_id": visitor.id,
            "nickname": visitor.nickname or "",
            "avatar_url": visitor.avatar_url or "",
        }

    def get_visitor_by_token(self, token: str) -> Visitor | None:
        try:
            payload = decode_access_token(token)
        except JWTError:
            return None
        subject = payload.get("sub", "")
        if not subject.startswith("visitor:"):
            return None
        visitor_id = int(subject.split(":", 1)[1])
        return self.db.get(Visitor, visitor_id)

    def update_profile(self, visitor_id: int, nickname: str | None = None, avatar_url: str | None = None) -> Visitor:
        visitor = self.db.get(Visitor, visitor_id)
        if visitor is None:
            raise ValueError("Visitor not found")
        if nickname is not None:
            visitor.nickname = nickname
        if is_temporary_avatar_url(avatar_url):
            raise ValueError("Temporary avatar URL cannot be saved")
        if avatar_url is not None:
            visitor.avatar_url = avatar_url
        self.db.commit()
        self.db.refresh(visitor)
        return visitor
