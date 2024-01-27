# coding=utf-8

import numpy as np
from numpy import ndarray
from pymilvus import (
    connections,
    Collection,
    utility,
)
from app.core.config import logger
from .configs import ClientConfig, basic_config, embedding_field, id_field
from ..inference.utils.checker import insert_data_check

__all__ = ["milvus_client"]

class MilvusClient:
    """
    MilvusClient to connect to Milvus server, create collection, insert entities, create index, search from docker
    """

    def __init__(
            self,
            flush_threshold: int = 100,
            refresh: bool = False,
            config: ClientConfig | None = None,
    ):
        if config:
            self._config: ClientConfig = config
        else:
            self._config: ClientConfig = basic_config
        logger.debug(f"\nMilvusClient init under config: {self._config}")
        self._flush_threshold = flush_threshold
        self._new_added = 0
        self._kwargs = {"refresh": refresh, 'flush_threshold': flush_threshold}
        self._connect_to_milvus()
        self.collection = self._create_collection()
        logger.debug("\nlist collections:")
        logger.debug(utility.list_collections())
        logger.debug(f"\nMlilvus init done.")

    def _connect_to_milvus(self):
        logger.debug(f"\nCreate connection...")
        connections.connect(
            host=self._config.host,
            port=self._config.port,
            timeout=120)
        logger.debug(f"\nList connections:")
        logger.debug(connections.list_connections())

    # 创建一个的集合
    def _create_collection(self) -> Collection:
        if (
                utility.has_collection(self._config.collection.name)
                and not self._kwargs["refresh"]
        ):
            logger.debug(f"\nFound collection: {self._config.collection.name}")
            # 2023-7-31 new: 如果存在直接返回 collection
            return Collection(self._config.collection.name)
        elif utility.has_collection(self._config.collection.name) and self._kwargs["refresh"]:
            logger.debug(
                f"\nFound collection: {self._config.collection.name}, deleting...")
            utility.drop_collection(self._config.collection.name)
            logger.debug(f"Collection {self._config.collection.name} deleted.")

        logger.debug(
            f"\nCollection {self._config.collection.name} is creating...")
        collection = Collection(**self._config.collection.as_dict())
        logger.debug("collection created:", self._config.collection.name)
        return collection

    def insert(self, entities: list[ndarray, ndarray, ndarray]):
        """

        :param entities: [[id:int64],[name:str,len<50],[normed_embedding:float32,shape(512,)]]
        :return:
        """
        # logger.debug 当前collection的数据量
        logger.debug(
            f"\nbefore_inserting,Collection:[{self._config.collection.name}] has {self.collection.num_entities} entities."
        )

        logger.debug("\nEntities check...")
        entities = insert_data_check(entities)
        logger.debug("\nInsert data...")
        self.collection.insert(entities)

        logger.debug(f"Done inserting new {len(entities[0])}data.")
        # TODO: schedule flush
        if not self.collection.has_index():  # 如果没有index，手动创建
            # Call the flush API to make inserted data immediately available
            # for search
            self.collection.flush()  # 新插入的数据在segment中达到一定阈值会自动构建index，持久化
            logger.debug("\nCreate index...")
            self._create_index()
            # 将collection 加载到到内存中
            logger.debug("\nLoad collection to memory...")
            self.collection.load()
            utility.wait_for_loading_complete(
                self._config.collection.name, timeout=10)
        else:
            # 由于没有主动调用flush, 只有达到一定阈值才会持久化 新插入的数据
            # 达到阈值后，会自动构建index，持久化，持久化后的新数据，才能正常的被加载到内存中，可以查找
            # 异步的方式加载数据到内存中，避免卡顿
            # 从而实现动态 一边查询，一边插入
            self._new_added += 1
            if self._new_added >= self._flush_threshold:
                logger.debug("\nFlush...")
                self.collection.flush()
                self._new_added = 0
                self.collection.load(_async=True)

        # logger.debug 当前collection的数据量
        logger.debug(
            f"after_inserting,Collection:[{self._config.collection.name}] has {self.collection.num_entities} entities."
        )
    # FIXME: failed
    # 向集合中插入实体

    def insert_from_files(self, file_paths: list):  # failed
        logger.debug("\nInsert data...")
        # 3. insert entities
        task_id = utility.do_bulk_insert(
            collection_name=self._config.collection.name,
            partition_name=self.collection.partitions[0].name,
            files=file_paths,
        )
        task = utility.get_bulk_insert_state(task_id=task_id)
        logger.debug("Task state:", task.state_name)
        logger.debug("Imported files:", task.files)
        logger.debug("Collection name:", task.collection_name)
        logger.debug("Start time:", task.create_time_str)
        logger.debug("Entities ID array generated by this task:", task.ids)
        while task.state_name != "Completed":
            task = utility.get_bulk_insert_state(task_id=task_id)
            logger.debug("Task state:", task.state_name)
            logger.debug("Imported row count:", task.row_count)
            if task.state == utility.BulkInsertState.ImportFailed:
                logger.debug("Failed reason:", task.failed_reason)
                raise Exception(task.failed_reason)
        self.collection.flush()
        logger.debug(self.get_entity_num)
        logger.debug("Done inserting data.")
        self._create_index()
        utility.wait_for_index_building_complete(self._config.collection.name)

    # 获取集合中的实体数量

    @property
    def get_entity_num(self):
        return self.collection.num_entities

    # 创建索引
    def _create_index(self):
        self.collection.create_index(
            field_name=embedding_field.name,
            index_params=self._config.index._asdict(),
        )
        # 检查索引是否创建完成
        utility.wait_for_index_building_complete(
            self._config.collection.name, timeout=60)
        logger.debug(
            "\nCreated index:\n{}".format(
                self.collection.index().params))

    # 搜索集合
    # noinspection PyTypeChecker
    def search(self, search_vectors: list[np.ndarray]) -> list[list[dict]]:
        # search_vectors可以是多个向量
        # logger.debug(f"\nSearching ...")
        results = self.collection.search(
            data=search_vectors, **self._config.search.as_dict()
        )
        # logger.debug("collecting results ...")
        ret_results = [[] for _ in range(len(results))]
        for i, hits in enumerate(results):
            for hit in hits:
                ret_results[i].append(
                    {
                        "score": hit.score,
                        "id": hit.entity.get('id'),
                        "name": hit.entity.get('name'),
                    }
                )
        # plogger.debug.plogger.debug(f"Search results : {ret_results}")
        return ret_results

    # 删除集合中的所有实体,并且关闭服务器
    # question: 可以不删除吗？下次直接读取上一次的内容？
    def shut_down(self):
        # 将仍未 持久化的数据持久化

        logger.debug(f"\nFlushing to seal the segment ...")
        self.collection.flush()
        # 释放内存
        self.collection.release()
        logger.debug(
            f"\nReleased collection : {self._config.collection.name} successfully !")
        # self.collection.drop_index()
        # logger.debug(f"Drop index: {self._collection_name} successfully !")
        # self.collection.drop()
        # logger.debug(f"Drop collection: {self._collection_name} successfully !")
        logger.debug(f"Stop MilvusClient successfully !")

    def has_collection(self):
        return utility.has_collection(self._config.collection.name)

    def __bool__(self):
        return self.get_entity_num > 0


milvus_client = MilvusClient()



if __name__ == "__main__":
    pass
