import enum

from app.services.llm_client import LLMClient

INTENT_PROMPT = """你是一个意图分类器。根据用户的问题，判断它属于以下哪个意图类别，只输出类别名称：

scenic_qa - 景区相关问答（景点介绍、历史、开放时间、票价等）
route_recommend - 路线推荐（怎么逛、带老人/小孩、推荐路线等）
service_query - 便民服务查询（餐厅、厕所、停车、交通等）
chitchat - 闲聊打招呼（你好、你是谁等非景区问题）

用户问题：{question}

意图类别："""


class Intent(enum.Enum):
    SCENIC_QA = "scenic_qa"
    ROUTE_RECOMMEND = "route_recommend"
    SERVICE_QUERY = "service_query"
    CHITCHAT = "chitchat"


VALID_INTENTS = {e.value for e in Intent}

ROUTE_KEYWORDS = (
    "路线",
    "游览顺序",
    "怎么逛",
    "推荐游",
    "半天",
    "一日游",
    "带老人",
    "带小孩",
    "亲子",
)
SERVICE_KEYWORDS = (
    "厕所",
    "卫生间",
    "餐厅",
    "吃饭",
    "停车",
    "停车场",
    "游客中心",
    "服务点",
    "附近",
)
CHITCHAT_KEYWORDS = ("你好", "您好", "你是谁", "谢谢", "再见")
SCENIC_QA_KEYWORDS = (
    "门票",
    "票价",
    "多少钱",
    "开放时间",
    "几点",
    "灵山",
    "大佛",
    "梵宫",
    "五印坛城",
)


class IntentClassifier:
    def __init__(self) -> None:
        self.llm_client = LLMClient()

    async def classify(self, question: str) -> Intent:
        rule_intent = self.classify_by_rules(question)
        if rule_intent is not None:
            return rule_intent

        try:
            prompt = INTENT_PROMPT.format(question=question)
            result = await self.llm_client.generate_text(prompt)
            intent_str = result.strip().lower()
            for valid in VALID_INTENTS:
                if valid in intent_str:
                    return Intent(valid)
        except Exception:
            pass
        return Intent.SCENIC_QA

    def classify_by_rules(self, question: str) -> Intent | None:
        normalized = (question or "").strip().lower()
        if not normalized:
            return Intent.SCENIC_QA
        if any(keyword in normalized for keyword in ROUTE_KEYWORDS):
            return Intent.ROUTE_RECOMMEND
        if any(keyword in normalized for keyword in SERVICE_KEYWORDS):
            return Intent.SERVICE_QUERY
        if any(keyword in normalized for keyword in CHITCHAT_KEYWORDS) and len(normalized) <= 12:
            return Intent.CHITCHAT
        if any(keyword in normalized for keyword in SCENIC_QA_KEYWORDS):
            return Intent.SCENIC_QA
        return None
