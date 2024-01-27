# coding=utf-8
"""
config stream handler and websocket handler for root logger
"""
import asyncio
import logging
from logging.handlers import QueueListener
from multiprocessing import Queue

log_queue = asyncio.Queue()

log_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')


class WebSocketHandler(logging.Handler):
    """websocket log handler"""

    def __init__(self):
        super().__init__()
        self.setFormatter(log_format)

    def emit(self, record):
        log_entry = self.format(record)
        log_queue.put_nowait(log_entry)


# root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# websocket handler
ws_handler = WebSocketHandler()
root_logger.addHandler(ws_handler)


# standard stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
root_logger.addHandler(stream_handler)


# shared queue for sub process
sub_process_msg_queue = Queue()

# listener for sub process logs ,msg handled by handlers
queue_listener = QueueListener(
    sub_process_msg_queue,
    ws_handler,
    stream_handler,
    respect_handler_level=True
)

logger = logging.getLogger(__name__)
