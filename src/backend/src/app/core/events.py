# coding=utf-8
"""
life span events
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from supabase_py_async import create_client
from supabase_py_async.lib.client_options import ClientOptions
from .config.logging_config import sub_process_msg_queue, queue_listener
from .supabase_client import supabase_client
from ..common import task_queue, registered_queue, result_queue
from ..services.inference.identifier import IdentifyWorker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ life span events"""
    identify_worker = None
    try:
        # start client
        load_dotenv()
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        supabase_client.client = await create_client(url, key, options=ClientOptions(
            postgrest_client_timeout=10, storage_client_timeout=10))
        assert supabase_client.client is not None

        # start identify worker
        identify_worker = IdentifyWorker(
            task_queue=task_queue,
            registered_queue=registered_queue,
            result_queue=result_queue,
            sub_process_msg_queue=sub_process_msg_queue
        )
        identify_worker.start()

        # start listener
        queue_listener.start()

        yield
    finally:
        if identify_worker:
            identify_worker.stop()
        queue_listener.stop()
