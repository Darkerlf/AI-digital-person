"""直接测试 Qwen API 对话能力 — 运行: python test_llm_direct.py"""
import asyncio
import sys
import os

# Fix Windows GBK encoding
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings
from app.services.llm_client import LLMClient


async def test_basic_chat():
    """测试基本对话"""
    print("=" * 50)
    print("测试1: 基本对话")
    print("=" * 50)

    client = LLMClient()
    result = await client.generate(
        system_prompt="你是灵山胜境景区的AI导游，请用简洁友好的语言回答。",
        user_message="你好，请简单介绍一下灵山大佛。",
    )
    print(f"回答: {result.text}")
    print(f"Token用量: prompt={result.prompt_tokens}, completion={result.completion_tokens}")
    print()


async def test_with_context():
    """测试带知识库上下文的对话"""
    print("=" * 50)
    print("测试2: 带上下文的RAG对话")
    print("=" * 50)

    client = LLMClient()
    context = """
[1] 灵山大佛高88米，位于江苏省无锡市滨湖区马山灵山路，是世界上最高的青铜佛像。
[2] 灵山大佛于1997年建成，佛像通高88米，其中佛体高79米，莲花座高9米。
[3] 灵山胜境景区门票价格：成人票210元，学生票105元。
"""
    result = await client.generate(
        system_prompt="你是灵山胜境景区的AI导游。基于参考资料回答，不要编造信息。",
        user_message="灵山大佛多高？什么时候建的？",
        context=context,
    )
    print(f"回答: {result.text}")
    print()


async def test_streaming():
    """测试流式输出"""
    print("=" * 50)
    print("测试3: 流式输出")
    print("=" * 50)
    print("回答: ", end="", flush=True)

    client = LLMClient()
    async for chunk in client.generate_stream(
        system_prompt="你是景区导游，用3句话介绍。",
        user_message="灵山胜境有什么好玩的？",
    ):
        print(chunk, end="", flush=True)
    print("\n")


async def test_embedding():
    """测试 Embedding 向量化"""
    print("=" * 50)
    print("测试4: 文本向量化 (Embedding)")
    print("=" * 50)

    from app.services.embedding_service import EmbeddingService
    svc = EmbeddingService()
    vector = await svc.embed_text("灵山大佛")
    print(f"向量维度: {len(vector)}")
    print(f"前5个值: {vector[:5]}")
    print()


async def main():
    print(f"API配置: model={settings.llm_model}, base_url={settings.llm_base_url}")
    print(f"API Key: {settings.dashscope_api_key[:10]}...")
    print()

    await test_basic_chat()
    await test_with_context()
    await test_streaming()
    await test_embedding()

    print("=" * 50)
    print("全部测试完成!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
