from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.conversation_repo import ConversationRepository
from app.repositories.knowledge_correction_repo import KnowledgeCorrectionRepository
from app.schemas.knowledge_correction import KnowledgeCorrectionTaskCreate


class KnowledgeCorrectionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.conversation_repo = ConversationRepository(db)
        self.repo = KnowledgeCorrectionRepository(db)

    def _to_read_dict(self, task) -> dict:
        return {
            "id": task.id,
            "source_message_id": task.source_message_id,
            "session_id": task.session_id,
            "scenic_area_id": task.scenic_area_id,
            "question_text": task.question_text,
            "recognized_text": task.recognized_text,
            "feedback_status": task.feedback_status,
            "correction_type": task.correction_type,
            "status": task.status,
            "resolution_note": task.resolution_note,
            "linked_faq_id": task.linked_faq_id,
            "linked_document_id": task.linked_document_id,
            "created_by": task.created_by,
            "resolved_by": task.resolved_by,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }

    def list_tasks(self) -> list[dict]:
        return [self._to_read_dict(task) for task in self.repo.list_tasks()]

    def get_task(self, task_id: int) -> dict:
        task = self.repo.get(task_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correction task not found")
        return self._to_read_dict(task)

    def create_task(self, payload: KnowledgeCorrectionTaskCreate, current_user) -> dict:
        if payload.correction_type not in {"faq", "document"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid correction type")

        message = self.conversation_repo.get_message(payload.source_message_id)
        if message is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation message not found")
        if self.repo.get_open_by_source_message_id(payload.source_message_id) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Correction task already exists")

        session = self.conversation_repo.get_session(message.session_id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        task = self.repo.create_from_message(message=message, session=session, payload=payload, created_by=current_user.id)
        return self._to_read_dict(task)

    def link_faq_and_resolve(self, correction_task_id: int, faq_id: int, current_user) -> dict:
        task = self.repo.get(correction_task_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correction task not found")
        if task.correction_type != "faq":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Correction task type mismatch")

        task.linked_faq_id = faq_id
        task.linked_document_id = None
        return self._resolve_task(task, current_user.id)

    def link_document_and_resolve(self, correction_task_id: int, document_id: int, current_user) -> dict:
        task = self.repo.get(correction_task_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correction task not found")
        if task.correction_type != "document":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Correction task type mismatch")

        task.linked_document_id = document_id
        task.linked_faq_id = None
        return self._resolve_task(task, current_user.id)

    def _resolve_task(self, task, resolved_by: int | None) -> dict:
        if task.linked_faq_id is None and task.linked_document_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Correction task has no linked result")

        message = self.conversation_repo.get_message(task.source_message_id)
        if message is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation message not found")

        task.status = "resolved"
        task.resolved_by = resolved_by
        message.resolution_status = "resolved"
        if task.resolution_note:
            message.resolution_note = task.resolution_note
        self.db.commit()
        self.db.refresh(task)
        return self._to_read_dict(task)
