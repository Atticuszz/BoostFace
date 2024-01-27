import numpy as np
from numpy import ndarray
from sympy import ShapeError


def insert_data_check(data: list[ndarray, ndarray, ndarray]) -> list:
    """
    check data before insert into milvus
    """
    ids, names, normed_embeddings = data
    # 不可以有缺失值
    if (
            (ids == "").any()
            or (names == "").any()
            or (normed_embeddings == np.NAN).any()
    ):
        raise ValueError('data cannot be ""or NAN')
    # 条目数必须相同
    if not (ids.shape[0]) == names.shape[0] == normed_embeddings.shape[0]:
        raise ValueError("data is not same length")
    # id必须是varchar
    if ids.dtype != str:
        ids = ids.astype(str)
    # id 必须唯一
    if np.unique(ids).shape[0] != ids.shape[0]:
        raise ShapeError("ids must be unique")
    # name必须是str
    if names.dtype != str:  # np.str: deprecated
        names = names.astype(str)
    # normed_embeddings必须是float32
    if normed_embeddings.dtype != np.float32:
        normed_embeddings = normed_embeddings.astype(np.float32)
    # normed_embeddings必须是512维
    if normed_embeddings.shape[1] != 512:
        raise ShapeError("normed_embeddings must be 512 dim")
    # normed_embeddings必须是 单位向量
    norms_after_normalization = np.linalg.norm(normed_embeddings, axis=1)
    is_normalized = np.allclose(norms_after_normalization, 1)
    if not is_normalized:
        raise ValueError("normed_embeddings must be normalized")
    # name长度不能超过50
    if not all([len(name) <= 50 for name in names]):
        raise ValueError("name length must be less than 50")

    # 提取成列表
    entries = [
        [_id for _id in ids],
        [name for name in names],
        [embedding for embedding in normed_embeddings],
    ]
    return entries
