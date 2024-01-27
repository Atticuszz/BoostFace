# coding=utf-8
import logging
from asyncio import sleep
from queue import Full

from fastapi import APIRouter, HTTPException,Body
from gotrue import Session, AuthResponse
from gotrue.errors import AuthApiError

from ..common import task_queue, registered_queue
from ..core.config import logger
from ..core.supabase_client import supabase_client
from ..schemas import UserLogin, Face2SearchSchema, Face2Search, UserRegister
from ..services.inference.common import TaskType

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login")
async def login(user: UserLogin) -> Session:
    """sign in with email and password"""
    try:
        response: AuthResponse = await supabase_client.sign_in(user.email, user.password)
        logger.info(f"User {user.email} logged in")
    except AuthApiError:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password")
    return response.session


@auth_router.post("/refresh-token")
async def refresh_token(refresh_token: str) -> Session:
    """refresh token"""
    try:
        new_session: AuthResponse = await supabase_client.refresh_session(refresh_token)
        logger.info(f"User {new_session.user.email} refreshed token")
        return new_session.session
    except AuthApiError:
        raise HTTPException(status_code=401, detail="Could not refresh token")


# TODO: how to register user with email and password
# TODO: add face passport register

# TODO: how to solve distribute results?
@auth_router.post("/face-register/{id}/{name}")
async def face_register(id: str, name: str, face: Face2SearchSchema = Body(...)) -> str:
    # resp = res
    to_register = Face2Search.from_schema(face).to_face()
    to_register.sign_up_id = id[:10]
    to_register.sign_up_name = name[:10]

    await task_queue.put_async((TaskType.REGISTER, to_register))

    return "face_register successfully!"


@auth_router.post("/register")
async def register(user: UserRegister) -> Session:
    """sign up with email and password"""
    try:
        response: AuthResponse = await supabase_client.sign_up(user.email, user.password, user.username)
        logger.info(f"User {user.email} signed up")
    except AuthApiError:
        raise HTTPException(
            status_code=400,
            detail="Invalid email or password")
    return response.session

