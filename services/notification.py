from collections import defaultdict
from asyncio import Queue

user_queue: dict[int, Queue] = {}

async def initiate_notification(recipient_id: int, payload: dict):
    if recipient_id in user_queue:
        await user_queue[recipient_id].put(payload)