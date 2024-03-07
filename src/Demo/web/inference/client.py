import asyncio
import json
import logging
from threading import Thread
from typing import Any

import cv2
import numpy as np
import websockets
from cv2 import Mat
from numpy import dtype, ndarray
from websockets import WebSocketClientProtocol

from ..settings import BACKEND_URL
from .types import WebsocketRSData
from .utils.decorator import error_handler

logger = logging.getLogger(__name__)


class WebSocketDataProcessor:
    """WebSocket data processor"""

    def _decode(
        self, data: str | bytes
    ) -> dict | str | Mat | ndarray[Any, dtype] | ndarray:
        """decode data"""
        raise NotImplementedError

    def _encode(self, data: dict | WebsocketRSData | str | bytes) -> str | bytes:
        """encode data"""
        raise NotImplementedError


class WebSocketBase(Thread, WebSocketDataProcessor):
    """
    WebSocket client for sending and receiving messages.

    Methods to be implemented by subclasses:
    - send(data): Sends data through the WebSocket.
    - receive(): Receives data from the WebSocket.
    - start(): Starts the WebSocket connection.
    - stop(): Stops the WebSocket connection.
    """

    def send(self, data: dict | WebsocketRSData | str | bytes):
        """
        Send data through the WebSocket.

        :param data: Data to be sent.
        """
        raise NotImplementedError

    def receive(self) -> dict | str | Mat | ndarray[Any, dtype] | ndarray | None:
        """
        Receive data from the WebSocket.

        Returns the received data.
        """
        raise NotImplementedError

    def start_ws(self):
        """
        Start the WebSocket connection as your want.
        """
        super().start()

    def stop_ws(self):
        """
        Stop the WebSocket connection.
        """
        raise NotImplementedError


class WebSocketClient(WebSocketBase):
    """WebsocketClient thread"""

    def __init__(self):
        super().__init__()
        self._is_running = False
        self.sender_queue = asyncio.Queue()
        self.receiver_queue = asyncio.Queue()
        self.ws_url = f"{BACKEND_URL}/identify/ws/"

    @error_handler
    def start_ws(self):
        """start websocket"""
        self._is_running = True
        super().start_ws()
        logger.info(f"{self.ws_url} : websocket started")

    @error_handler
    def stop_ws(self):
        """stop websocket"""
        if not self.is_alive():  # 检查线程是否已经开始
            logger.debug(f"WebSocket thread: has not been started or already stopped.")
            return
        self._is_running = False
        self.sender_queue.put_nowait("STOP")
        self.join()
        logger.info(f"{self.ws_url} : websocket stopped")

    @error_handler
    def send(self, data: dict | WebsocketRSData | str | bytes):
        """send data to websocket"""
        try:
            self.sender_queue.put_nowait(data)
        except asyncio.QueueFull:
            logger.warning(f"{self.ws_url} : sender queue is full")

    @error_handler
    def receive(self) -> dict | str | Mat | ndarray[Any, dtype] | ndarray | None:
        """receive data from websocket"""
        try:
            return self.receiver_queue.get_nowait()
        except asyncio.QueueEmpty:
            # logger.warning(f"{self.ws_url} : receiver queue is empty")
            return None

    @error_handler
    def run(self):
        """run websocket"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._connect_websocket())

    @error_handler
    async def _connect_websocket(self):
        """connect websocket"""

        logger.debug(f"{self.ws_url} : websocket connecting")
        async with websockets.connect(self.ws_url) as websocket:
            consumer_task = asyncio.create_task(self._receive_messages(websocket))
            producer_task = asyncio.create_task(self._send_messages(websocket))
            logger.debug(f"{self.ws_url} : websocket connected")
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_EXCEPTION,
            )

            for task in pending:
                task.cancel()

    @error_handler
    # @profile
    async def _receive_messages(self, websocket: WebSocketClientProtocol):
        logger.debug(f"start receive messages")
        while self._is_running:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                decoded = self._decode(message)
                await self.receiver_queue.put(decoded)
            except asyncio.TimeoutError:
                logger.debug(f"{self.ws_url} : receive timeout")
                continue
            except websockets.exceptions.ConnectionClosedError:
                logger.info(f"{self.ws_url} : Connection closed")
                break
            except Exception as e:
                logger.error(f"WebSocket error occurred: {e.__class__.__name__} - {e}")

    @error_handler
    # @profile
    async def _send_messages(self, websocket: WebSocketClientProtocol):
        logger.debug(f"start send messages")
        while self._is_running:
            try:
                data = await self.sender_queue.get()
                if data == "STOP":
                    break
                encoded = self._encode(data)
                await websocket.send(encoded)
                self.sender_queue.task_done()
            except websockets.exceptions.ConnectionClosedError:
                logger.info(f"{self.ws_url} : Connection closed")
                break
            except Exception as e:
                logger.error(f"WebSocket error occurred: {e.__class__.__name__} - {e}")

    @error_handler
    def _decode(
        self, data: str | bytes
    ) -> dict | str | Mat | ndarray[Any, dtype] | ndarray:
        if isinstance(data, bytes):
            # image
            nd_arr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nd_arr, cv2.IMREAD_COLOR)
            return img
        elif isinstance(data, str):
            try:
                # dict
                decoded = json.loads(data)

                if not isinstance(decoded, dict):
                    logger.debug(f"recv str data:{data},should be dict")
                    raise TypeError(f"can not decode data:{data}")
                logger.debug(f"recv dict data:{decoded}")
                return decoded
            except json.JSONDecodeError:
                # pure utf-8 string
                logger.debug(f"recv str data:{data}")
                return data
        else:
            raise TypeError(f"can not decode data:{data}")

    @error_handler
    def _encode(self, data: dict | WebsocketRSData | str | bytes) -> str | bytes:
        if isinstance(data, WebsocketRSData):
            if data is None:
                logger.error(f"can not encode data:{data}")
            return data.to_schema().model_dump_json()
        elif isinstance(data, dict):
            return json.dumps(data)
        elif isinstance(data, str) or isinstance(data, bytes):
            return data
        else:
            raise TypeError(f"can not encode data:{data}")
