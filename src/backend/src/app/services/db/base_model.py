# coding=utf-8
from dataclasses import dataclass
from enum import StrEnum



# for search_param
# Similarity Metrics
# https://milvus.io/docs/metric.md#Euclidean-distance-L2


class SimilarityMetric(StrEnum):
    """ Similarity metrics for floating point embeddings """
    EUCLIDEAN = "L2"  # Euclidean distance
    INNER_PRODUCT = "IP"  # Inner product
    COSINE = "COSINE"  # Cosine similarity


class FloatingPointIndexType(StrEnum):
    """ Index types for floating-point embeddings """
    FLAT = "FLAT"  # Relatively small dataset, requires 100% recall rate
    IVF_FLAT = "IVF_FLAT"  # High-speed query, high recall rate
    GPU_IVF_FLAT = "GPU_IVF_FLAT"  # High-speed query, high recall rate, uses GPU
    IVF_SQ8 = "IVF_SQ8"  # High-speed query, limited memory, minor recall rate compromise
    # Very high-speed query, limited memory, substantial recall rate compromise
    IVF_PQ = "IVF_PQ"
    # Very high-speed query, limited memory, substantial recall rate
    # compromise, uses GPU
    GPU_IVF_PQ = "GPU_IVF_PQ"
    HNSW = "HNSW"  # Very high-speed query, very high recall rate, large memory resources
    SCANN = "SCANN"  # Very high-speed query, very high recall rate, large memory resources


class BinaryIndexType(StrEnum):
    """ Index types for binary embeddings """
    BIN_FLAT = "BIN_FLAT"  # Small datasets, perfect accuracy, exact search results
    BIN_IVF_FLAT = "BIN_IVF_FLAT"  # High-speed query, high recall rate


class DistanceMetric(StrEnum):
    """ Distance metrics for binary embeddings """
    JACCARD = "Jaccard"
    HAMMING = "Hamming"


@dataclass
class MatchedResult:
    id: str
    name: str
    score: float
    time: str
    face_id: str | None = None



