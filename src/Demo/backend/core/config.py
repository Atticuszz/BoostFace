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
import os
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, ConfigDict, Field
from pydantic_settings import BaseSettings

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


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SUPABASE_URL: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL"))
    SUPABASE_KEY: str = Field(default_factory=lambda: os.getenv("SUPABASE_KEY"))
    SUPERUSER_EMAIL: str = Field(default_factory=lambda: os.getenv("SUPERUSER_EMAIL"))
    SUPERUSER_PASSWORD: str = Field(default=lambda: os.getenv("SUPERUSER_PASSWORD"))
    # SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    SERVER_PORT: int = 8000
    # # TODO: the following  need to follow the newest version of fastapi
    # # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    #
    # @validator("BACKEND_CORS_ORIGINS", pre=True)
    # def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
    #     if isinstance(v, str) and not v.startswith("["):
    #         return [i.strip() for i in v.split(",")]
    #     elif isinstance(v, (list, str)):
    #         return v
    #     raise ValueError(v)
    #
    PROJECT_NAME: str = "fastapi supabase template"

    # class Config(ConfigDict):
    #     """sensitive to lowercase"""
    #
    #     case_sensitive = True
    Config: ClassVar[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)


settings = Settings()
