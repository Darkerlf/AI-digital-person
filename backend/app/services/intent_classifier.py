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


class IntentClassifier:
    def __init__(self) -> None:
        self.llm_client = LLMClient()

    async def classify(self, question: str) -> Intent:
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
