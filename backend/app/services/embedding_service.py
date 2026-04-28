from openai import AsyncOpenAI

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.llm_base_url,
        )
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension

    async def embed_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            return [0.0] * self.dimension
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]
