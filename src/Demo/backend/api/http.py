from fastapi import APIRouter, Body

from ..common import task_queue
from ..schemas import Face2Search, Face2SearchSchema
from ..services.inference.common import TaskType

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# TODO: add face passport register
# TODO: how to solve distribute results?
# TODO: register face with id and name use sessionDepend
@auth_router.post("/face-register/{id}/{name}")
async def face_register(id: str, name: str, face: Face2SearchSchema = Body(...)) -> str:
    """
    register face with id and name
    """
    # resp = res
    to_register = Face2Search.from_schema(face).to_face()
    to_register.sign_up_id = id[:10]
    to_register.sign_up_name = name[:10]

    await task_queue.put_async((TaskType.REGISTER, to_register))

    return "face_register successfully!"


