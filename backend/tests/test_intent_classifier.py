import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.services.intent_classifier import IntentClassifier, Intent


@pytest.fixture
def classifier():
    return IntentClassifier()


class TestIntentClassifier:
    def test_rule_based_ticket_question_skips_llm(self):
        classifier = IntentClassifier()
        mock_generate = AsyncMock(return_value="route_recommend")

        with patch.object(classifier.llm_client, "generate_text", mock_generate):
            intent = asyncio.run(classifier.classify("\u95e8\u7968\u591a\u5c11\u94b1"))

        assert intent == Intent.SCENIC_QA
        mock_generate.assert_not_awaited()

    def test_rule_based_route_question_skips_llm(self):
        classifier = IntentClassifier()
        mock_generate = AsyncMock(return_value="scenic_qa")

        with patch.object(classifier.llm_client, "generate_text", mock_generate):
            intent = asyncio.run(classifier.classify("\u63a8\u8350\u6e38\u89c8\u8def\u7ebf"))

        assert intent == Intent.ROUTE_RECOMMEND
        mock_generate.assert_not_awaited()

    def test_rule_based_service_question_skips_llm(self):
        classifier = IntentClassifier()
        mock_generate = AsyncMock(return_value="scenic_qa")

        with patch.object(classifier.llm_client, "generate_text", mock_generate):
            intent = asyncio.run(classifier.classify("\u9644\u8fd1\u6709\u5395\u6240\u5417"))

        assert intent == Intent.SERVICE_QUERY
        mock_generate.assert_not_awaited()

    def test_rule_based_greeting_skips_llm(self):
        classifier = IntentClassifier()
        mock_generate = AsyncMock(return_value="scenic_qa")

        with patch.object(classifier.llm_client, "generate_text", mock_generate):
            intent = asyncio.run(classifier.classify("\u4f60\u597d"))

        assert intent == Intent.CHITCHAT
        mock_generate.assert_not_awaited()

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
