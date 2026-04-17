from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.core.database import get_db
from app.schemas.conversation import (
    ConversationSessionDetail,
    ConversationSessionListItem,
    ResolveConversationMessageRequest,
    UnresolvedConversationItem,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("")
def list_sessions(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    items = ConversationService(db).list_sessions()
    return {"items": [ConversationSessionListItem.model_validate(item).model_dump(mode="json") for item in items]}


@router.get("/unresolved")
def list_unresolved(_: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    items = ConversationService(db).list_unresolved_messages()
    return {"items": [UnresolvedConversationItem.model_validate(item).model_dump(mode="json") for item in items]}


@router.get("/{session_id}", response_model=ConversationSessionDetail)
def get_session(session_id: int, _: object = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return ConversationService(db).get_session_detail(session_id)


@router.put("/messages/{message_id}/resolve")
def resolve_message(
    message_id: int,
    payload: ResolveConversationMessageRequest,
    _: object = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return ConversationService(db).resolve_message(message_id, payload)
