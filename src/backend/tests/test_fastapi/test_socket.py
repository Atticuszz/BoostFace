"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 16/12/2023
@Description  :
"""
# test_app.py
from fastapi.testclient import TestClient
from src.app.main import app
import asyncio


client = TestClient(app)


def test_websocket():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("Hello, WebSocket!")
        data = websocket.receive_text()
        assert data == "Message text was: Hello, WebSocket!"
