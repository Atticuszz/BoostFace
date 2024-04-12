from contextlib import asynccontextmanager

from fastapi import WebSocket
from pydantic import BaseModel
from starlette.websockets import WebSocketState

from ..core.config import logger


class WebSocketManager:
    """WebSocket manager"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    @asynccontextmanager
    async def handle_connection(self, websocket: WebSocket):
        """Handle connection."""
        logger.debug(f"handle_connection called...")
        await self.connect(websocket)
        try:
            yield websocket
        finally:
            await self.disconnect(websocket)

    async def connect(self, websocket: WebSocket):
        """Connect with category."""
        logger.info(f"connecting {len(self.active_connections)}th client...")
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        """Disconnect."""
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
        index = self.active_connections.index(websocket)
        self.active_connections.remove(websocket)
        logger.info(f"disconnecting {index}th client...")

    # async def broadcast(self, message: str):
    #     """Broadcast message to all connections or specific category.
    #     :exception ConnectionClosedOK, ConnectionClosedError
    #     """
    #     for typed_ws in self.active_connections:
    #         # note: the active connection may be closed ,we need to check it
    #         if (
    #                 category is None or typed_ws.category == category
    #         ) and typed_ws.ws.client_state == WebSocketState.CONNECTED:
    #             await typed_ws.ws.send_text(message)


class WebSocketConnection:
    """auto handle data send and receive"""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def send_data(self, data: BaseModel | str):
        """Send data as JSON or str
        :exception TypeError,RuntimeError
        """
        if isinstance(data, BaseModel):
            await self.websocket.send_text(data.model_dump_json())
        elif isinstance(data, str):
            await self.websocket.send_text(data)
        else:
            raise TypeError("data must be BaseModel or str")

    async def receive_data(
        self, data_model: type[BaseModel] | None = None
    ) -> BaseModel | str:
        """Receive and decode data.
        :exception TypeError，RuntimeError
        """
        if data_model is None:
            received_data = await self.websocket.receive_text()
            return received_data
        elif issubclass(data_model, BaseModel):
            received_data = await self.websocket.receive_text()
            return data_model.model_validate_json(received_data)
        else:
            raise TypeError("data_model must be a subclass of BaseModel or None")


def websocket_endpoint():
    """Decorator for websocket endpoints."""
    logger.debug("websocket_endpoint called...")

    def decorator(func):
        async def wrapper(websocket: WebSocket):
            async with web_socket_manager.handle_connection(websocket) as ws:
                connection = WebSocketConnection(ws)
                return await func(connection)

        return wrapper

    return decorator


web_socket_manager = WebSocketManager()
