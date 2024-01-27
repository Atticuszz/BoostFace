"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 21/12/2023
@Description  :
"""
import logging
from pathlib import Path

import cv2

from src.app.common.client import client
from src.app.utils.boostface.common import ImageFaces
from src.app.utils.boostface.component.detector import DetectorBase

IMAGE_PATH = r'C:\Users\18317\python\BoostFace_fastapi\src\boostface\db\data\test_01\known'

# paper: 高并发注册人脸

import aiohttp
import asyncio

async def sign_up(session, base_url, face2register, id, name):
    url = f'{base_url}/auth/face-register/{id}/{name}'
    headers = {'Content-Type': 'application/json'}
    data = face2register.model_dump()
    async with session.post(url, json=data, headers=headers) as response:
        return await response.text()  # 或者根据你的需求调整返回值
class Register:
    def __init__(self, src_dir: Path, base_url: str):
        self.detector = DetectorBase()
        self.img_path = src_dir.glob('*')
        self.base_url = base_url

    async def work(self):
        i = 0
        tasks = []
        async with aiohttp.ClientSession() as session:
            for file in self.img_path:
                img = cv2.imread(file.as_posix())
                if img is None:
                    continue
                det = ImageFaces(image=img, faces=[])
                res = self.detector.run_onnx(det)  # 假设这不是异步的
                if not res:
                    continue
                for face in res.faces:
                    try:
                        face.sign_up_info.id = face.id
                        face.sign_up_info.name = file.stem
                        face_img = face.face_image(res.nd_arr)
                        task = asyncio.ensure_future(sign_up(session, self.base_url, face_img.to_schema(), id=face.sign_up_info.id, name=face.sign_up_info.name))
                        tasks.append(task)
                        logging.debug(f"Total add to signed up: {i}")
                        if len(tasks) >= 100:
                            await asyncio.gather(*tasks)
                            tasks = []
                        i += 1
                    except Exception as e:
                        logging.error(f"Error during sign up: {e}")
            if tasks:
                await asyncio.gather(*tasks)  # 为剩余任务等待
            logging.debug(f"Total signed up: {i}")
#
# class Register:
#     def __init__(self, src_dir: Path):
#         self.detector = DetectorBase()
#         self.img_path = src_dir.glob('*')
#         self.sign_up = client.sign_up
#
#     def work(self):
#         i = 0
#         for file in self.img_path:
#             img = cv2.imread(file.as_posix())
#             det = ImageFaces(image=img, faces=[])
#             res: ImageFaces = self.detector.run_onnx(det)
#             for face in res.faces:
#                 try:
#                     face.sign_up_info.id = face.id
#                     face.sign_up_info.name = file.stem
#                     face_img = face.face_image(res.nd_arr)
#                     self.sign_up(face_img.to_schema(), id=face.sign_up_info.id, name=face.sign_up_info.name)
#                     i+=1
#                     logging.debug(f"sign up {i}th")
#                 except:
#                     pass



if __name__=="__main__":
    src_dir = Path(IMAGE_PATH)

    register = Register(src_dir, client.base_url)
    asyncio.run(register.work())
