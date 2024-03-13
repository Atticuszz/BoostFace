from enum import Enum
from pathlib import Path

__all__ = [
    "ModelsConfig",
    "SourceConfig",
    "CameraConfig",
    "InferenceProvider",
    "DetectorConfig",
]

from typing import NamedTuple

DATA_ROOT = Path(__file__).parent / "data"
VIDEO_ROOT = DATA_ROOT / "video"
IMAGE_ROOT = DATA_ROOT / "image"
MODEL_ROOT = DATA_ROOT / "model"

BACKEND_URL = "ws://localhost:5000"


class SourceConfig(Enum):
    video: str = "video"
    # Image: str = "image"
    Webcam: str = "Webcam"

    def files(self) -> list[Path | int]:
        if self == SourceConfig.video:
            return list(VIDEO_ROOT.glob("*.mp4"))
        # elif self == SourceConfig.Image:
        #     return list(IMAGE_ROOT.glob("*.jpg"))
        elif self == SourceConfig.Webcam:
            return [0]
        else:
            raise ValueError(f"Invalid source: {self}")


class CameraConfig(NamedTuple):
    """
    config for Camera
    """

    url: str | int = 0
    url_type: SourceConfig = SourceConfig.Webcam
    fps: int = 30
    resolution: tuple[int, ...] = (640, 480)


# (640, 480) 25
#  (1024, 768) 10
# (1280, 720) 5
# (1600, 1200) 5
# (1920, 1080) 5
# (2560, 1440) 5


class InferenceProvider(Enum):
    GPU: int = 0
    CPU: int = 1


class DetectorConfig(NamedTuple):
    provider: InferenceProvider = InferenceProvider.GPU
    threshold: float = 0.5


class TrackerConfig(NamedTuple):
    """
    :param max_age: del as frames not matched
    :param iou_threshold: for Hungarian algorithm
    """

    iou_threshold: float = 0.3
    max_age: int = 30
    scale_threshold: float = 0.005
    frames_threshold: int = 100
    min_hits: int = 3

    def __str__(self):
        return f"iou_threshold: {self.iou_threshold}, max_age: {self.max_age}, scale_threshold: {self.scale_threshold}, frames_threshold: {self.frames_threshold}, min_hits: {self.min_hits}"


class ModelsConfig(Enum):
    detect_model: str = "det_2.5g.onnx"
    extract_model: str = "irn50_glint360k_r50.onnx"

    def path(self) -> Path:
        return MODEL_ROOT / self.value
