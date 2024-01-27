# coding=utf-8
import asyncio
import logging
import multiprocessing
from multiprocessing.queues import Queue
from queue import Full, Empty
from typing import NamedTuple, Callable

from fastapi import WebSocket


class TypedWebSocket(NamedTuple):
    client_id: str
    category: str
    ws: WebSocket


class AsyncProcessQueue(Queue):
    def __init__(self, maxsize=1000):
        ctx = multiprocessing.get_context()
        super().__init__(maxsize, ctx=ctx)

    async def put_async(self, item):
        return await self._continued_try(self.put_nowait, item)

    async def get_async(self):
        return await self._continued_try(self.get_nowait)

    async def _continued_try(self, operation: Callable, *args):
        while True:
            try:
                return operation(*args)
            except Full:
                logging.debug("Queue is full")
                await asyncio.sleep(0.01)
            except Empty:
                logging.debug("Queue is empty")
                await asyncio.sleep(0.01)


task_queue = AsyncProcessQueue()  # Queue[tuple[TaskType, Face]
result_queue = AsyncProcessQueue()  # Queue[MatchedResult]
registered_queue = AsyncProcessQueue()  # Queue[str]
