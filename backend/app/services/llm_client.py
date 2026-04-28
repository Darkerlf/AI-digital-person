from dataclasses import dataclass

from openai import AsyncOpenAI

from app.core.config import settings


@dataclass
class LLMResult:
    text: str
    prompt_tokens: int
    completion_tokens: int


class LLMClient:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.llm_base_url,
        )
        self.model = settings.llm_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature

    def _build_messages(
        self,
        system_prompt: str,
        user_message: str,
        context: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        if context:
            user_content = f"以下是参考资料：\n{context}\n\n用户问题：{user_message}"
        else:
            user_content = user_message
        messages.append({"role": "user", "content": user_content})
        return messages

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        context: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> LLMResult:
        messages = self._build_messages(system_prompt, user_message, context, history)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResult(
            text=choice.message.content or "",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
        )

    async def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        context: str | None = None,
        history: list[dict[str, str]] | None = None,
    ):
        messages = self._build_messages(system_prompt, user_message, context, history)
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content

    async def generate_text(self, prompt: str) -> str:
        """Simple single-prompt generation (used by intent classifier)."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.1,
        )
        return response.choices[0].message.content or ""
