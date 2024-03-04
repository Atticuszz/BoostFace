import asyncio
from queue import Empty

from fastapi import APIRouter
from gotrue import Session
from starlette.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from ..common import result_queue, task_queue
from ..core import WebSocketConnection, websocket_endpoint
from ..core.config import logger
from ..schemas import Face2Search, Face2SearchSchema, IdentifyResult, SystemStats
from ..services.db.base_model import MatchedResult
from ..services.inference.common import TaskType


identify_router = APIRouter(prefix="/identify", tags=["identify"])


@identify_router.websocket("/ws/")
@websocket_endpoint()
async def identify_ws(connection: WebSocketConnection):
    while True:
        # test identifyResult
        try:
            rec_data = await connection.receive_data(Face2SearchSchema)
            logger.debug("rec_data:", rec_data)
            search_data = Face2Search.from_schema(rec_data)
            logger.debug(f"get the search data:{search_data}")

            await task_queue.put_async((TaskType.IDENTIFY, search_data.to_face()))

            try:
                res: MatchedResult = await result_queue.get_async()
                result = IdentifyResult.from_matched_result(res)
                await connection.send_data(result)
            except Empty:
                logger.warn("empty in result queue")

            # time_now = datetime.datetime.now()
            # result = IdentifyResult(
            #     id=str(uuid.uuid4()),
            #     name=session.user.user_metadata.get("name"),
            #     time=time_now.strftime("%Y-%m-%d %H:%M:%S"),
            #     uid=search_data.uid,
            #     score=0.99
            # )

            # await asyncio.sleep(1)  # 示例延时
        except (
                ConnectionClosedOK,
                ConnectionClosedError,
                RuntimeError,
                WebSocketDisconnect,
        ) as e:
            logger.info(f"WebSocket error occurred: {e.__class__.__name__} - {e}")
            logger.info(f"Client left the chat")
            break


@identify_router.websocket("/test/ws/{client_id}")
@websocket_endpoint()
async def test_connect(connection: WebSocketConnection, session: Session):
    """cloud_system_monitor websocket"""
    while True:
        try:
            data = await connection.receive_data()
            logger.debug(f"test websocket receive data:{data}")
            await connection.send_data(data)
            logger.debug(f"test websocket send data:{data}")
        except (
                ConnectionClosedOK,
                ConnectionClosedError,
                RuntimeError,
                WebSocketDisconnect,
        ) as e:
            logger.info(f"occurred error {e} Client {session.user.id} left the chat")
            break
