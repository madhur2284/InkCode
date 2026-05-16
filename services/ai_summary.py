from openai import AsyncOpenAI
from config import settings
import asyncio
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from models.db_models import Post
from crud.post import update_summary
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=settings().NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

async def generate_ai_summary(post_id: int, title: str, content: str):
    try:
        model="mistralai/mistral-medium-3.5-128b"

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                     "content": """You are a technical blog summarizer.
                        Your job is to write a concise 2-3 sentence summary 
                        of blog posts. The summary should:
                        - Capture the main topic and key insight
                        - Be written for a developer audience
                        - Not start with "This post" or "This article"
                        - Be plain text, no markdown
                        Return ONLY the summary, nothing else."""
                },
                {
                    "role": "user",
                    "content": f"Title: {title}, Content: {content}"
                }
            ],
            temperature=0.2,
            max_tokens=300
        )

        summary = response.choices[0].message.content.strip()
        async with AsyncSessionLocal() as db:
            result = await update_summary(db, summary, post_id)
            return result.get("message", "")     
    except Exception as e:
        logger.error("summary Generation Failed")
    


if __name__ == "__main__":
    asyncio.run(generate_ai_summary(post_id=0, title="Async Python Beyond Syntax: Event Loops, Backpressure, and Concurrency at Scale", content = """Async programming in Python is often misunderstood as merely adding async and await keywords, but the real power lies in how the event loop orchestrates cooperative multitasking. Unlike thread-based concurrency, asyncio minimizes context-switching overhead by allowing coroutines to voluntarily yield control during I/O waits. This makes it highly efficient for network-heavy systems such as API gateways, websocket servers, distributed crawlers, and real-time streaming applications.

However, production-grade async systems require deeper understanding than coroutine syntax. Poorly managed tasks can create hidden bottlenecks through event loop starvation, unbounded task spawning, or blocking synchronous calls inside coroutines. Concepts like backpressure, cancellation propagation, connection pooling, and structured concurrency become critical when scaling services.

Python’s async ecosystem has also evolved significantly. Libraries like FastAPI, httpx, asyncpg, and uvicorn leverage ASGI and non-blocking sockets to deliver high concurrency with relatively low resource consumption. Meanwhile, uvloop replaces the default event loop with a libuv-backed implementation, dramatically improving throughput and latency.

The key insight is that async is not about making code “faster” universally; it is about maximizing efficiency during idle waiting periods. Understanding where concurrency helps—and where multiprocessing or threading is more appropriate—is what separates scalable backend engineering from superficial async usage."""))
    