"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 08/02/2024
@Description  :
"""
import logging
from pathlib import Path

from pygizmokit import download_files

LFW_URL = (
    "https://github.com/Atticuszz/BoostFace/releases/download/v0.0.1/LFW_dataset.zip"
)
ONNXURL = "https://github.com/Atticuszz/BoostFace_fastapi/releases/download/v0.0.1/irn50_glint360k_r50.onnx"

SCRFD_URL = [
    "https://github.com/Atticuszz/BoostFace_pyqt6/releases/download/v0.0.1/det_10g.onnx",
    "https://github.com/Atticuszz/BoostFace_pyqt6/releases/download/v0.0.1/det_2.5g.onnx",
]

PROXY = {
    "http": "http://192.168.0.107:7890",
    "https": "http://192.168.0.107:7890",
}


def check_file_exist(dir: Path, file_name: str) -> bool:
    """
    check if the file exists
    :param dir: the file path
    :return: True if the file exists
    """
    assert (
        isinstance(dir, Path) and isinstance(file_name, str) or not dir.is_dir()
    ), "Invalid input"
    for file in dir.rglob("*"):
        if file.name == file_name:
            logging.info(f"{file_name} already exists")
            return True
    return False


def download_lfw(output_dir: Path | None = None) -> None:
    """Download LFW dataset"""
    if output_dir is None:
        output_dir = Path(__file__).parents[1] / "dataset_loader" / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    if check_file_exist(output_dir, "lfw-deepfunneled"):
        return

    download_files([LFW_URL], output_dir=output_dir, proxies=PROXY)


def download_onnx(output_dir: Path | None = None) -> None:
    """Download ONNX model"""
    if output_dir is None:
        output_dir = Path(__file__).parents[1] / "inference" / "model_zoo" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    if check_file_exist(output_dir, "irn50_glint360k_r50.onnx"):
        return

    download_files([ONNXURL], output_dir=output_dir, proxies=PROXY)


def download_scrfd(output_dir: Path | None = None) -> None:
    """Download SCRFD model"""
    if output_dir is None:
        output_dir = Path(__file__).parents[1] / "inference" / "model_zoo" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    if check_file_exist(output_dir, "det_2.5g.onnx") and check_file_exist(
        output_dir, "det_10g.onnx"
    ):
        return

    download_files(SCRFD_URL, output_dir=output_dir, proxies=PROXY)


if __name__ == "__main__":
    download_lfw()
    download_onnx()
    download_scrfd()
    logging.info("download done!")
