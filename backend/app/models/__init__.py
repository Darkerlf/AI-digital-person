from app.models.admin_user import AdminUser
from app.models.ai_provider_config import AIProviderConfig
from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.dashboard_stat_daily import DashboardStatDaily
from app.models.digital_human_config import DigitalHumanConfig
from app.models.faq_item import FAQItem
from app.models.feedback_record import FeedbackRecord
from app.models.import_job import ImportJob
from app.models.import_job_item import ImportJobItem
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument
from app.models.operation_log import OperationLog
from app.models.scenic_area import ScenicArea
from app.models.scenic_spot import ScenicSpot
from app.models.scenic_spot_tag import ScenicSpotTag
from app.models.visitor_behavior_event import VisitorBehaviorEvent


def load_all_models() -> None:
    _ = (
        AdminUser,
        AIProviderConfig,
        ConversationMessage,
        ConversationSession,
        DashboardStatDaily,
        DigitalHumanConfig,
        FAQItem,
        FeedbackRecord,
        ImportJob,
        ImportJobItem,
        KnowledgeChunk,
        KnowledgeDocument,
        OperationLog,
        ScenicArea,
        ScenicSpot,
        ScenicSpotTag,
        VisitorBehaviorEvent,
    )
