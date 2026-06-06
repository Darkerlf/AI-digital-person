"""自动演示 AI 导游对话 — 运行: python test_chat_demo.py"""
import asyncio
import sys
import os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))

from app.services.rag_pipeline import RAGPipeline, SYSTEM_PROMPT
from app.services.intent_classifier import IntentClassifier
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import load_all_models


DEMO_QUESTIONS = [
    "你好，你是谁？",
    "灵山大佛多高？是什么材质做的？",
    "带老人去灵山胜境，有什么推荐的游览路线吗？",
    "景区里有餐厅吗？",
    "门票多少钱？",
]


async def main():
    print("=" * 55)
    print("   灵山胜境 AI 数字人导游 — 自动演示")
    print("=" * 55)
    print()

    load_all_models()
    engine = create_engine("sqlite:///demo_chat.db", future=True)
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)()

    rag = RAGPipeline(db)
    classifier = IntentClassifier()
    history = []

    intent_labels = {
        "scenic_qa": "景区问答",
        "route_recommend": "路线推荐",
        "service_query": "便民服务",
        "chitchat": "闲聊",
    }

    for i, question in enumerate(DEMO_QUESTIONS, 1):
        print(f"问题 {i}: {question}")

        intent = await classifier.classify(question)
        print(f"  意图识别: {intent_labels.get(intent.value, intent.value)}")

        print(f"  AI回答: ", end="", flush=True)
        full_answer = ""
        async for chunk in rag.answer_stream(question, history=history):
            print(chunk, end="", flush=True)
            full_answer += chunk
        print("\n")

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": full_answer})

    db.close()
    print("=" * 55)
    print("  演示结束!")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
