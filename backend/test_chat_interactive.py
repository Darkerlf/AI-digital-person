"""交互式景区AI导游对话 — 运行: python test_chat_interactive.py"""
import asyncio
import sys
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stdin.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))

from app.services.rag_pipeline import RAGPipeline, SYSTEM_PROMPT
from app.services.intent_classifier import IntentClassifier
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import load_all_models


async def main():
    print("=" * 50)
    print("  灵山胜境 AI 数字人导游 (终端版)")
    print("=" * 50)
    print("输入问题与AI导游对话，输入 'quit' 退出")
    print()

    # Use SQLite for demo (no MySQL needed)
    load_all_models()
    engine = create_engine("sqlite:///demo_chat.db", future=True)
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)()

    rag = RAGPipeline(db)
    classifier = IntentClassifier()
    history = []

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input or user_input.lower() == "quit":
            break

        # Intent classification
        intent = await classifier.classify(user_input)
        intent_map = {
            "scenic_qa": "景区问答",
            "route_recommend": "路线推荐",
            "service_query": "便民服务",
            "chitchat": "闲聊",
        }
        print(f"  [意图: {intent_map.get(intent.value, intent.value)}]")

        # Generate answer
        print("AI: ", end="", flush=True)
        full_answer = ""
        async for chunk in rag.answer_stream(user_input, history=history):
            print(chunk, end="", flush=True)
            full_answer += chunk
        print("\n")

        # Update history
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": full_answer})
        if len(history) > 20:
            history = history[-20:]

    db.close()
    print("再见！")


if __name__ == "__main__":
    asyncio.run(main())
