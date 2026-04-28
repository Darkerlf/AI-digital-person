from unittest.mock import MagicMock, patch

import pytest

from app.services.embedding_service import EmbeddingService


@pytest.fixture
def embedding_service():
    return EmbeddingService()


class TestEmbeddingService:
    @pytest.mark.asyncio
    async def test_embed_text_returns_vector(self, embedding_service):
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1024)]

        with patch.object(
            embedding_service.client.embeddings, "create", return_value=mock_response
        ):
            vector = await embedding_service.embed_text("灵山大佛")
        assert len(vector) == 1024
        assert isinstance(vector, list)
        assert all(isinstance(v, float) for v in vector)

    @pytest.mark.asyncio
    async def test_embed_batch_returns_multiple_vectors(self, embedding_service):
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1024),
            MagicMock(embedding=[0.2] * 1024),
        ]

        with patch.object(
            embedding_service.client.embeddings, "create", return_value=mock_response
        ):
            vectors = await embedding_service.embed_batch(["文本1", "文本2"])
        assert len(vectors) == 2
        assert len(vectors[0]) == 1024

    @pytest.mark.asyncio
    async def test_embed_empty_text_returns_zero_vector(self, embedding_service):
        vector = await embedding_service.embed_text("")
        assert len(vector) == 1024
        assert all(v == 0.0 for v in vector)
