import logging

import cv2
from fastapi import APIRouter, Body

from ..common import task_queue
from ..schemas import Face2Search, Face2SearchSchema
from ..services.inference.common import TaskType

auth_router = APIRouter(prefix="/auth", tags=["auth"])

#
# def _draw_bbox(dimg, bbox, bbox_color=(0, 255, 0)):
#     """
#     only draw the bbox beside the corner,and the corner is round
#     :param dimg: img to draw bbox on
#     :param bbox: face bboxes
#     """
#     # 定义矩形的四个角的坐标
#     pt1 = list(map(int, bbox[0]))
#     pt2 = list(map(int, bbox[3]))
#     bbox_thickness = 4
#     # 定义直角附近线段的长度
#     line_len = int(0.08 * (pt2[0] - pt1[0]) + 0.06 * (pt2[1] - pt1[1]))
#
#     def draw_line(_pt1, _pt2):
#         cv2.line(dimg, _pt1, _pt2, bbox_color, bbox_thickness)
#
#     draw_line((pt1[0], pt1[1]), (pt1[0] + line_len, pt1[1]))
#     draw_line((pt1[0], pt1[1]), (pt1[0], pt1[1] + line_len))
#     draw_line((pt2[0], pt1[1]), (pt2[0] - line_len, pt1[1]))
#     draw_line((pt2[0], pt1[1]), (pt2[0], pt1[1] + line_len))
#     draw_line((pt1[0], pt2[1]), (pt1[0] + line_len, pt2[1]))
#     draw_line((pt1[0], pt2[1]), (pt1[0], pt2[1] - line_len))
#     draw_line((pt2[0], pt2[1]), (pt2[0] - line_len, pt2[1]))
#     draw_line((pt2[0], pt2[1]), (pt2[0], pt2[1] - line_len))
#     return dimg

@auth_router.post("/face-register/{id}/{name}")
async def face_register(id: str, name: str, face: Face2SearchSchema = Body(...)) -> str:
    """
    register face with uid and name
    """
    # resp = res
    # logging.info(f"date received: {face}")
    to_register = Face2Search.from_schema(face).to_face()
    # img_debug = _draw_bbox(to_register.img, face.model_extra["bbox"])
    #
    # cv2.imshow("face", img_debug)
    #
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    to_register.sign_up_id = id[:10]
    to_register.sign_up_name = name[:10]

    await task_queue.put_async((TaskType.REGISTER, to_register))

    return "face_register successfully!"
