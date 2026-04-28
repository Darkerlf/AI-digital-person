"""Tests for LLM client — uses mocked HTTP responses."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.llm_client import LLMClient


@pytest.fixture
def llm_client():
    return LLMClient()


class TestLLMClient:
    def test_build_client_with_default_config(self, llm_client):
        assert llm_client.client is not None

    @pytest.mark.asyncio
    async def test_generate_returns_text(self, llm_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="灵山大佛高88米"))]
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=20)

        with patch.object(
            llm_client.client.chat.completions, "create",
            new_callable=AsyncMock, return_value=mock_response,
        ):
            result = await llm_client.generate(
                system_prompt="你是景区导游",
                user_message="灵山大佛多高？",
            )
        assert result.text == "灵山大佛高88米"
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 20

    @pytest.mark.asyncio
    async def test_generate_with_context(self, llm_client):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="回答"))]
        mock_response.usage = MagicMock(prompt_tokens=10, completion_tokens=5)

        with patch.object(
            llm_client.client.chat.completions, "create",
            new_callable=AsyncMock, return_value=mock_response,
        ) as mock_create:
            await llm_client.generate(
                system_prompt="你是景区导游",
                user_message="问题",
                context="相关知识片段",
            )
            call_args = mock_create.call_args
            messages = call_args.kwargs["messages"]
            assert any("相关知识片段" in m["content"] for m in messages)

    @pytest.mark.asyncio
    async def test_generate_stream_yields_chunks(self, llm_client):
        chunk1 = MagicMock()
        chunk1.choices = [MagicMock(delta=MagicMock(content="你好"), finish_reason=None)]
        chunk2 = MagicMock()
        chunk2.choices = [MagicMock(delta=MagicMock(content="世界"), finish_reason="stop")]

        async def mock_stream():
            for chunk in [chunk1, chunk2]:
                yield chunk

        with patch.object(
            llm_client.client.chat.completions, "create",
            new_callable=AsyncMock, return_value=mock_stream(),
        ):
            chunks = []
            async for text in llm_client.generate_stream(
                system_prompt="你是景区导游",
                user_message="你好",
            ):
                chunks.append(text)
            assert chunks == ["你好", "世界"]
