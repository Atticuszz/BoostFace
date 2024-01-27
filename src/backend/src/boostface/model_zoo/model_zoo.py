# -*- coding: utf-8 -*-
# @Organization  : insightface.ai
# @Author        : Jia Guo
# @Time          : 2021-05-04
# @Function      : 

from pathlib import Path

from .arcface_onnx import *
from .attribute import Attribute
from .inswapper import INSwapper
from .landmark import *
from .retinaface import *
from .scrfd import *

__all__ = ['get_model']


class PickableInferenceSession(onnxruntime.InferenceSession):
    # This is a wrapper to make the current InferenceSession class pickable.
    def __init__(self, model_path, **kwargs):
        super().__init__(model_path, **kwargs)
        self.model_path = model_path

    def __getstate__(self):
        return {'model_path': self.model_path}

    def __setstate__(self, values):
        model_path = values['model_path']
        self.__init__(model_path)


class ModelRouter:
    def __init__(self, onnx_file):
        self.onnx_file = onnx_file

    def get_model(self, **kwargs):
        session = PickableInferenceSession(str(self.onnx_file), **kwargs)
        print(f'Applied providers: {session._providers}, with options: {session._provider_options}')
        inputs = session.get_inputs()
        input_cfg = inputs[0]
        input_shape = input_cfg.shape
        outputs = session.get_outputs()

        if len(outputs) >= 5:
            return SCRFD(model_file=self.onnx_file, session=session)
        elif input_shape[2] == 192 and input_shape[3] == 192:
            return Landmark(model_file=self.onnx_file, session=session)
        elif input_shape[2] == 96 and input_shape[3] == 96:
            return Attribute(model_file=self.onnx_file, session=session)
        elif len(inputs) == 2 and input_shape[2] == 128 and input_shape[3] == 128:
            return INSwapper(model_file=self.onnx_file, session=session)
        elif input_shape[2] == input_shape[3] and input_shape[2] >= 112 and input_shape[2] % 16 == 0:
            return ArcFaceONNX(model_file=self.onnx_file, session=session)
        else:
            # raise RuntimeError('error on model routing')
            return None


def find_onnx_file(dir_path: Path):
    if not dir_path.exists():
        return None
    paths = list(dir_path.parent.glob("*.onnx"))
    if len(paths) == 0:
        return None
    return paths


def get_default_providers():
    return ['CUDAExecutionProvider', 'CPUExecutionProvider']


def get_default_provider_options():
    return None


def get_model(model_root: Path, **kwargs):
    if model_root.suffix != '.onnx':  # 没有那就从默认路径中再找一遍
        model_file = find_onnx_file(model_root)
        if model_file is None:
            return None
    else:
        model_file = model_root
    assert model_file.exists(), f'model_file {model_file} should exist'
    assert model_file.is_file(), f'model_file {model_file} should be a file'
    router = ModelRouter(model_file)
    providers = kwargs.get('providers', get_default_providers())
    provider_options = kwargs.get('provider_options', get_default_provider_options())
    model = router.get_model(providers=providers, provider_options=provider_options)
    return model
