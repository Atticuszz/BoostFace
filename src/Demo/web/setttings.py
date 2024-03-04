from enum import Enum
from pathlib import Path

__all__ = ["Settings", "SourceConfig", "ModelsConfig"]

from typing import NamedTuple

DATA_ROOT = Path(__file__).parent / "data"
VIDEO_ROOT = DATA_ROOT / "video"
IMAGE_ROOT = DATA_ROOT / "image"
MODEL_ROOT = DATA_ROOT / "model"

BACKEND_URL = "ws://localhost:5000"


class SourceConfig(Enum):
    video: str = "video"
    Image: str = "image"
    Webcam: str = "Webcam"

    def files(self) -> list[Path] | int:
        if self == SourceConfig.video:
            return list(VIDEO_ROOT.glob("*.mp4"))
        elif self == SourceConfig.Image:
            return list(IMAGE_ROOT.glob("*.jpg"))
        elif self == SourceConfig.Webcam:
            return 0
        else:
            raise ValueError(f"Invalid source: {self}")


class CameraConfig(NamedTuple):
    """
    config for Camera
    """

    fps: int = 30
    resolution: tuple[int, ...] = (1920, 1080)
    url: SourceConfig = SourceConfig.video


class ModelsConfig(Enum):
    detect_model: str = "det_2.5g.onnx"
    extract_model: str = "irn50_glint360k_r50.onnx"

    def path(self) -> Path:
        return MODEL_ROOT / self.value


class Settings(Enum):
    model = ModelsConfig
    source = SourceConfig
