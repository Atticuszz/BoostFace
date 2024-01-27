import pprint
from typing import NamedTuple

from pymilvus import DataType, CollectionSchema, FieldSchema

from .base_model import SimilarityMetric, DistanceMetric, FloatingPointIndexType, BinaryIndexType


def recursive_as_dict(obj):
    if hasattr(obj, 'as_dict') and callable(getattr(obj, 'as_dict')):
        # 如果对象有 as_dict 方法，使用它
        return obj.as_dict()
    elif hasattr(obj, '_asdict') and callable(getattr(obj, '_asdict')):
        # 对于 NamedTuple，使用 _asdict 方法
        return {k: recursive_as_dict(v) for k, v in obj._asdict().items()}
    elif isinstance(obj, dict):
        # 对于字典，递归处理每个值
        return {k: recursive_as_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # 对于列表，递归处理每个元素
        return [recursive_as_dict(v) for v in obj]
    else:
        # 否则直接返回值
        return obj

# TODO: dataclass would be better
# for collection initialization
class Field(NamedTuple):
    name: str
    dtype: DataType
    description: str = ''
    is_primary: bool = False
    max_length: int | None = None
    dim: int | None = None

    def as_dict(self) -> dict:
        """
        filter out None value
        :return:
        """
        return {k: v for k, v in self._asdict().items() if v is not None}

    # 想象成pandas的DataFrame，列名是字段名，每一行是一个实体，实体由不同的字段组成


##########################################################################
# 2. field view
# +-+------------+------------+------------------+------------------------------+
# | | "pk"      | "random"   |    "embeddings"   |
# +-+------------+------------+------------------+------------------------------+
# |1|  VarChar  |    Double  |    FloatVector    |
# +-+------------+------------+------------------+------------------------------+
# |2|  VarChar  |    Double  |    FloatVector    |
# +-+------------+------------+------------------+------------------------------+
# |3|| VarChar  |    Double  |    FloatVector    |
# +-+------------+------------+------------------+------------------------------+
##############################################################################
# Data type of the data to insert must **match the schema of the collection**
# otherwise Milvus will raise exception.
class CollectionConfig(NamedTuple):
    name: str
    schema: CollectionSchema
    shards_num: int
    properties: dict[str, str | int] = {"collection.ttl.seconds": 0}

    def as_dict(self) -> dict:
        """
        filter out None value and convert NamedTuple to dict
        :return:
        """
        filtered: dict = {k: v for k, v in self._asdict().items() if v is not None}
        return recursive_as_dict(filtered)


class PreparedSearchParam(NamedTuple):
    metric_type: SimilarityMetric | DistanceMetric = SimilarityMetric.INNER_PRODUCT
    params: dict[str, int] = {"nlist:": 1024, "nprobe": 10}


class IndexParam(NamedTuple):
    index_type: FloatingPointIndexType | BinaryIndexType = FloatingPointIndexType.IVF_FLAT
    metric_type: SimilarityMetric | DistanceMetric = SimilarityMetric.INNER_PRODUCT
    params: dict[str, int] = {"nlist:": 1024, "nprobe": 10}


class searchParam(NamedTuple):
    """
    _async，_callback异步编程相关
    search doesn't support vector field as output_fields
    """
    param: PreparedSearchParam
    anns_field: CollectionConfig.name
    limit: int  # number of returned results
    # fields to return in the query result
    output_fields: list[Field.name]
    partition_names: list[str] | None = None
    expr: str | None = None  # query expression ?unclear

    def as_dict(self) -> dict:
        """
        filter out None value and convert NamedTuple to dict
        :return:
        """
        filtered: dict = {k: v for k, v in self._asdict().items() if v is not None}
        return recursive_as_dict(filtered)


class ClientConfig(NamedTuple):
    collection: CollectionConfig
    index: IndexParam
    search: searchParam
    port: int = 19530
    host: str = "localhost"

    def as_dict(self) -> dict:
        """
        filter out None value and convert NamedTuple to dict
        :return:
        """
        filtered: dict = {k: v for k, v in self._asdict().items() if v is not None}
        return recursive_as_dict(filtered)


id_field = Field(
    name="id",
    dtype=DataType.VARCHAR,
    max_length=40,
    description="primary key",
    is_primary=True)
name_field = Field(
    name="name",
    dtype=DataType.VARCHAR,
    max_length=20,
    description="name of the person")
embedding_field = Field(
    name="embedding",
    dtype=DataType.FLOAT_VECTOR,
    description="embedding of the face",
    dim=512)

fields = [FieldSchema(**field.as_dict())
          for field in [id_field, name_field, embedding_field]]

basic_config = ClientConfig(
    collection=CollectionConfig(
        name="Faces",
        schema=CollectionSchema(
            fields=fields,
            description="Faces collection",
            enable_dynamic_field=True
        ),
        shards_num=6,
    ),
    index=IndexParam(
        index_type=FloatingPointIndexType.IVF_FLAT,
        metric_type=SimilarityMetric.INNER_PRODUCT,
        params={"nlist": 1024, "nprobe": 10}  # 定义了搜索时候的 聚类数量
    ),
    search=searchParam(
        param=PreparedSearchParam(
            metric_type=SimilarityMetric.INNER_PRODUCT,
            params={"nlist": 1024, "nprobe": 10}
        ),
        anns_field="embedding",
        limit=1,
        output_fields=["id", 'name']
    )
)
if __name__ == "__main__":
    # 务必确保对外只呈现字典或者枚举类型，这样才能作为配置参数
    pprint.pprint(basic_config.as_dict())
