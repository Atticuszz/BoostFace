"""
life span events
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..common import registered_queue, result_queue, task_queue
from ..core.config import logger
from ..services.inference.identifier import IdentifyWorker
from .config import queue_listener, sub_process_msg_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    """life span events"""
    identify_worker = None
    try:
        logger.info("starting identify worker...")
        # start identify worker
        identify_worker = IdentifyWorker(
            task_queue=task_queue,
            registered_queue=registered_queue,
            result_queue=result_queue,
            sub_process_msg_queue=sub_process_msg_queue,
        )
        identify_worker.start()

        # start listener
        queue_listener.start()

        yield
    finally:
        if identify_worker:
            identify_worker.stop()
        queue_listener.stop()
