from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.knowledge_correction_task import KnowledgeCorrectionTask
from app.schemas.knowledge_correction import KnowledgeCorrectionTaskCreate


class KnowledgeCorrectionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_tasks(
        self,
        *,
        status: str | None = None,
        correction_type: str | None = None,
        scenic_area_id: int | None = None,
    ) -> list[KnowledgeCorrectionTask]:
        statement = select(KnowledgeCorrectionTask)
        if status:
            statement = statement.where(KnowledgeCorrectionTask.status == status)
        if correction_type:
            statement = statement.where(KnowledgeCorrectionTask.correction_type == correction_type)
        if scenic_area_id is not None:
            statement = statement.where(KnowledgeCorrectionTask.scenic_area_id == scenic_area_id)
        statement = statement.order_by(KnowledgeCorrectionTask.id.desc())
        return self.db.execute(statement).scalars().all()

    def get(self, task_id: int) -> KnowledgeCorrectionTask | None:
        return self.db.get(KnowledgeCorrectionTask, task_id)

    def get_open_by_source_message_id(self, source_message_id: int) -> KnowledgeCorrectionTask | None:
        return (
            self.db.execute(
                select(KnowledgeCorrectionTask).where(
                    KnowledgeCorrectionTask.source_message_id == source_message_id,
                    KnowledgeCorrectionTask.status == "open",
                )
            )
            .scalars()
            .first()
        )

    def create_from_message(
        self,
        message: ConversationMessage,
        session: ConversationSession,
        payload: KnowledgeCorrectionTaskCreate,
        created_by: int | None,
    ) -> KnowledgeCorrectionTask:
        task = KnowledgeCorrectionTask(
            source_message_id=message.id,
            session_id=session.id,
            scenic_area_id=session.scenic_area_id,
            question_text=message.question_text,
            recognized_text=message.recognized_text,
            feedback_status=message.feedback_status,
            correction_type=payload.correction_type,
            status="open",
            resolution_note=payload.resolution_note,
            linked_faq_id=None,
            linked_document_id=None,
            created_by=created_by,
            resolved_by=None,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
