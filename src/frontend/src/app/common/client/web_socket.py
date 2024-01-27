import asyncio
import datetime
import json
from threading import Thread
from typing import Any

import cv2
import numpy as np
import websockets
from cv2 import Mat
from numpy import ndarray, dtype
from websockets import WebSocketClientProtocol

from src.app.common.types import WebsocketRSData
from .client import client
from ...config import qt_logger
from ...utils.decorator import error_handler
from ...utils.time_tracker import time_tracker


class WebSocketDataProcessor:
    """WebSocket data processor"""

    def _decode(self, data: str |
                bytes) -> dict | str | Mat | ndarray[Any, dtype] | ndarray:
        """decode data"""
        raise NotImplementedError

    def _encode(self, data: dict | WebsocketRSData |
                str | bytes) -> str | bytes:
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

    def receive(
            self) -> dict | str | Mat | ndarray[Any, dtype] | ndarray | None:
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

    def __init__(self, ws_type: str | None = None):
        super().__init__()
        self._is_running = False
        self.ws_type: str | None = ws_type
        self.sender_queue = asyncio.Queue()
        self.receiver_queue = asyncio.Queue()
        self.base_url = f"{client.base_ws_url}/identify/{self.ws_type}/ws/"
        self.auth_header = client._auth_header()

    @error_handler
    def start_ws(self):
        """ start websocket"""
        self._is_running = True
        super().start_ws()
        qt_logger.info(f"{self.base_url} : websocket started")

    @error_handler
    def stop_ws(self):
        """stop websocket"""
        if not self.is_alive():  # 检查线程是否已经开始
            qt_logger.debug(f"WebSocket thread:{self.ws_type}has not been started or already stopped.")
            return
        self._is_running = False
        self.sender_queue.put_nowait("STOP")
        self.join()
        qt_logger.info(f"{self.base_url} : websocket stopped")

    @error_handler
    def send(self, data: dict | WebsocketRSData | str | bytes):
        """send data to websocket"""
        try:
            self.sender_queue.put_nowait(data)
        except asyncio.QueueFull:
            qt_logger.warning(f"{self.base_url} : sender queue is full")

    @error_handler
    def receive(
            self) -> dict | str | Mat | ndarray[Any, dtype] | ndarray | None:
        """receive data from websocket"""
        try:
            return self.receiver_queue.get_nowait()
        except asyncio.QueueEmpty:
            qt_logger.warning(f"{self.base_url} : receiver queue is empty")
            return None

    @error_handler
    def run(self):
        """ run websocket"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._connect_websocket())

    @error_handler
    async def _connect_websocket(self):
        """connect websocket"""
        time_now = datetime.datetime.now()
        client_id: str = client.user['id'] + time_now.strftime('%Y%m%d%H%M%S')
        uri = self.base_url + client_id
        qt_logger.debug(f"{self.base_url} : websocket connecting")
        async with websockets.connect(uri, extra_headers=self.auth_header) as websocket:
            consumer_task = asyncio.create_task(
                self._receive_messages(websocket))
            producer_task = asyncio.create_task(self._send_messages(websocket))
            qt_logger.debug(f"{self.base_url} : websocket connected")
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_EXCEPTION,
            )

            for task in pending:
                task.cancel()

    @error_handler
    async def _receive_messages(self, websocket: WebSocketClientProtocol):
        qt_logger.debug(f"{self.base_url} : start receive messages")
        while self._is_running:

            try:
                with time_tracker.track(f"{self.base_url} : receive messages"):
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    decoded = self._decode(message)
                    await self.receiver_queue.put(decoded)
            except asyncio.TimeoutError:
                qt_logger.debug(f"{self.base_url} : receive timeout")
                continue
            except websockets.exceptions.ConnectionClosedError:
                qt_logger.info(f'{self.base_url} : Connection closed')
                break
            except Exception as e:
                qt_logger.error(f"WebSocket error occurred: {e.__class__.__name__} - {e}")

    @error_handler
    async def _send_messages(self, websocket: WebSocketClientProtocol):
        qt_logger.debug(f"{self.base_url} : start send messages")
        while self._is_running:
            try:
                with time_tracker.track(f"{self.base_url}send messages"):
                    data = await self.sender_queue.get()
                    if data == "STOP":
                        break
                    encoded = self._encode(data)
                    await websocket.send(encoded)
                    self.sender_queue.task_done()
            except websockets.exceptions.ConnectionClosedError:
                qt_logger.info(f'{self.base_url} : Connection closed')
                break
            except Exception as e:
                qt_logger.error(f"WebSocket error occurred: {e.__class__.__name__} - {e}")

    @error_handler
    def _decode(self, data: str |
                bytes) -> dict | str | Mat | ndarray[Any, dtype] | ndarray:
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
                    qt_logger.debug(f"recv str data:{data},should be dict")
                    raise TypeError(f"can not decode data:{data}")
                qt_logger.debug(f"recv dict data:{decoded}")
                return decoded
            except json.JSONDecodeError:
                # pure utf-8 string
                qt_logger.debug(f"recv str data:{data}")
                return data
        else:
            raise TypeError(f"can not decode data:{data}")

    @error_handler
    def _encode(self, data: dict | WebsocketRSData |
                str | bytes) -> str | bytes:
        if isinstance(data, WebsocketRSData):
            if data is None:
                qt_logger.error(f"can not encode data:{data}")
            return data.to_schema().model_dump_json()
        elif isinstance(data, dict):
            return json.dumps(data)
        elif isinstance(data, str) or isinstance(data, bytes):
            return data
        else:
            raise TypeError(f"can not encode data:{data}")
