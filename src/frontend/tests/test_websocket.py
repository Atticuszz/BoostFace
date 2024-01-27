"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 16/12/2023
@Description  :
"""
import asyncio
import datetime

from time import sleep

import pytest
import websockets

from src.app.common.client import client
from src.app.common.client.web_socket import WebSocketClient


def test_WebSocketClient():
    client = WebSocketClient("test")
    client.start_ws()
    client.send("Hello, WebSocket!")
    sleep(1)
    data = client.receive()
    assert data == "Hello, WebSocket!"


@pytest.mark.asyncio
async def test_websocket_manager():
    base_url = 'ws://127.0.0.1:5000/identify/test/ws/'
    time_now = datetime.datetime.now()
    client_id: str = client.user['id'] + time_now.strftime('%Y%m%d%H%M%S')
    uri = base_url + client_id
    async with websockets.connect(uri, extra_headers=client._auth_header()) as websocket:

        await websocket.send("Hello, WebSocket!")
        data = await websocket.recv()
        assert data == "Hello, WebSocket!"
