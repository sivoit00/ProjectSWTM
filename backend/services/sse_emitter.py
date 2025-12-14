import json
import asyncio

class SSEEmitter:
    """Ein einfacher SSE-Emitter"""
    def __init__(self):
        self.queue = asyncio.Queue()

    async def send(self, event: str, data: dict):
        payload = f"event: {event}\ndata: {json.dumps(data)}\n\n"
        await self.queue.put(payload)

    async def stream(self):
        while True:
            msg = await self.queue.get()
            if msg is None:
                break
            yield msg.encode("utf-8")

    async def close(self):
        await self.queue.put(None)
