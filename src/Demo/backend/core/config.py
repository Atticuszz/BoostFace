"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 05/01/2024
@Description  :
"""

import logging
from logging.handlers import QueueListener
from multiprocessing import Queue

from dotenv import load_dotenv
from pygizmokit.rich_logger import set_up_logging

"""
config stream handler and websocket handler for root logger
"""

log_format = logging.Formatter("%(asctime)s : %(levelname)s - %(message)s")

# root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# standard stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_format)
root_logger.addHandler(stream_handler)

# shared queue for sub process
sub_process_msg_queue = Queue()

# listener for sub process logs ,msg handled by handlers
queue_listener = QueueListener(
    sub_process_msg_queue, stream_handler, respect_handler_level=True
)

logger = logging.getLogger(__name__)

load_dotenv()
set_up_logging()
