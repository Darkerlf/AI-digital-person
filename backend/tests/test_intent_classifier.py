from unittest.mock import AsyncMock, patch

import pytest

from app.services.intent_classifier import IntentClassifier, Intent


@pytest.fixture
def classifier():
    return IntentClassifier()


class TestIntentClassifier:
    @pytest.mark.asyncio
    async def test_classify_scenic_qa(self, classifier):
        with patch.object(classifier.llm_client, "generate_text", new_callable=AsyncMock, return_value="scenic_qa"):
            intent = await classifier.classify("灵山大佛多高？")
        assert intent == Intent.SCENIC_QA

    @pytest.mark.asyncio
    async def test_classify_route_recommend(self, classifier):
        with patch.object(classifier.llm_client, "generate_text", new_callable=AsyncMock, return_value="route_recommend"):
            intent = await classifier.classify("带老人怎么逛？")
        assert intent == Intent.ROUTE_RECOMMEND

    @pytest.mark.asyncio
    async def test_classify_chitchat(self, classifier):
        with patch.object(classifier.llm_client, "generate_text", new_callable=AsyncMock, return_value="chitchat"):
            intent = await classifier.classify("你好啊")
        assert intent == Intent.CHITCHAT

    @pytest.mark.asyncio
    async def test_classify_service_query(self, classifier):
        with patch.object(classifier.llm_client, "generate_text", new_callable=AsyncMock, return_value="service_query"):
            intent = await classifier.classify("附近有餐厅吗？")
        assert intent == Intent.SERVICE_QUERY

    @pytest.mark.asyncio
    async def test_classify_unknown_defaults_to_scenic_qa(self, classifier):
        with patch.object(classifier.llm_client, "generate_text", new_callable=AsyncMock, return_value="something_else"):
            intent = await classifier.classify("随便什么")
        assert intent == Intent.SCENIC_QA

    @pytest.mark.asyncio
    async def test_classify_error_defaults_to_scenic_qa(self, classifier):
        with patch.object(classifier.llm_client, "generate_text", new_callable=AsyncMock, side_effect=Exception("API error")):
            intent = await classifier.classify("问题")
        assert intent == Intent.SCENIC_QA
