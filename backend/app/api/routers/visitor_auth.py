from fastapi import APIRouter, Depends, File as FastAPIFile, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.visitor_service import VisitorService
from app.utils.object_storage import get_object_storage

router = APIRouter(prefix="/tourist", tags=["tourist"])
bearer_scheme = HTTPBearer(auto_error=False)
ALLOWED_AVATAR_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_BYTES = 2 * 1024 * 1024


class WxUserInfo(BaseModel):
    nickname: str | None = Field(default=None, alias="nickName")
    avatar_url: str | None = Field(default=None, alias="avatarUrl")

    model_config = ConfigDict(populate_by_name=True)


class WxLoginRequest(BaseModel):
    code: str
    user_info: WxUserInfo | None = None


class WxLoginResponse(BaseModel):
    token: str
    visitor_id: int
    nickname: str
    avatar_url: str


class UpdateProfileRequest(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None


class ProfileResponse(BaseModel):
    visitor_id: int
    nickname: str
    avatar_url: str


def _get_current_visitor(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    visitor = VisitorService(db).get_visitor_by_token(credentials.credentials)
    if visitor is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid visitor token")
    return visitor


@router.post("/wx-login", response_model=WxLoginResponse)
async def wx_login(payload: WxLoginRequest, db: Session = Depends(get_db)):
    service = VisitorService(db)
    try:
        result = await service.login_by_wechat(
            payload.code,
            nickname=payload.user_info.nickname if payload.user_info else None,
            avatar_url=payload.user_info.avatar_url if payload.user_info else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return WxLoginResponse(**result)


@router.get("/profile", response_model=ProfileResponse)
def get_profile(visitor=Depends(_get_current_visitor)):
    return ProfileResponse(
        visitor_id=visitor.id,
        nickname=visitor.nickname or "",
        avatar_url=visitor.avatar_url or "",
    )


@router.put("/profile", response_model=ProfileResponse)
def update_profile(payload: UpdateProfileRequest, visitor=Depends(_get_current_visitor), db: Session = Depends(get_db)):
    service = VisitorService(db)
    try:
        updated = service.update_profile(visitor.id, nickname=payload.nickname, avatar_url=payload.avatar_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ProfileResponse(
        visitor_id=updated.id,
        nickname=updated.nickname or "",
        avatar_url=updated.avatar_url or "",
    )


@router.post("/profile/avatar", response_model=ProfileResponse)
async def upload_avatar(
    avatar: UploadFile = FastAPIFile(...),
    visitor=Depends(_get_current_visitor),
    db: Session = Depends(get_db),
):
    content_type = avatar.content_type or ""
    if content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Avatar file type is not supported")

    data = await avatar.read(MAX_AVATAR_BYTES + 1)
    if len(data) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Avatar file exceeds 2 MiB")
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Avatar file is empty")

    storage = get_object_storage()
    if not storage.is_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OSS storage is not configured")

    filename = avatar.filename or "avatar"
    try:
        stored = storage.upload_bytes(
            data,
            filename=filename,
            prefix="visitor-avatars",
            content_type=content_type,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Avatar upload failed") from exc

    updated = VisitorService(db).update_profile(visitor.id, avatar_url=stored.url)
    return ProfileResponse(
        visitor_id=updated.id,
        nickname=updated.nickname or "",
        avatar_url=updated.avatar_url or "",
    )
