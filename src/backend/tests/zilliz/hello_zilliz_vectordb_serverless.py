import asyncio
import configparser
import time
import random
from pymilvus import connections, utility
from pymilvus import Collection, DataType, FieldSchema, CollectionSchema


async def async_search(collection: Collection, search_vec, search_params, topk, book_intro_field):
    # 使用异步搜索
    future = collection.search(search_vec,
                               anns_field=book_intro_field.name,
                               param=search_params,
                               limit=topk,
                               guarantee_timestamp=1,
                               _async=True)
    # 等待搜索完成
    results = await future
    return results


if __name__ == '__main__':
    # connect to milvus
    cfp = configparser.RawConfigParser()
    cfp.read('config_serverless.ini')
    milvus_uri = cfp.get('example', 'uri')
    token = cfp.get('example', 'token')

    connections.connect("default",
                        uri=milvus_uri,
                        token=token,
                        timeout=30)
    print(f"Connecting to DB: {milvus_uri}")

    # Check if the collection exists
    collection_name = "books"
    check_collection = utility.has_collection(collection_name)
    if check_collection:
        drop_result = utility.drop_collection(collection_name)
    print("Success!")
    # create a collection with customized primary field: book_id_field
    dim = 64
    book_id_field = FieldSchema(
        name="book_id",
        dtype=DataType.INT64,
        is_primary=True,
        description="customized primary id")
    word_count_field = FieldSchema(
        name="word_count",
        dtype=DataType.INT64,
        description="word count")
    book_intro_field = FieldSchema(
        name="book_intro",
        dtype=DataType.FLOAT_VECTOR,
        dim=dim)
    schema = CollectionSchema(
        fields=[
            book_id_field,
            word_count_field,
            book_intro_field],
        auto_id=False,
        description="my first collection")
    print(f"Creating example collection: {collection_name}")
    collection = Collection(name=collection_name, schema=schema)
    print(f"Schema: {schema}")
    print("Success!")

    # insert data with customized ids
    nb = 1000
    insert_rounds = 2
    start = 0  # first primary key id
    total_rt = 0  # total response time for inert
    print(f"Inserting {nb * insert_rounds} entities... ")
    for i in range(insert_rounds):
        book_ids = [i for i in range(start, start + nb)]
        word_counts = [random.randint(1, 100) for i in range(nb)]
        book_intros = [[random.random() for _ in range(dim)]
                       for _ in range(nb)]
        entities = [book_ids, word_counts, book_intros]
        t0 = time.time()
        ins_resp = collection.insert(entities)
        ins_rt = time.time() - t0
        start += nb
        total_rt += ins_rt
    print(f"Succeed in {round(total_rt, 4)} seconds!")
    # print(f"collection {collection_name} entities: {collection.num_entities}")

    # flush
    print("Flushing...")
    start_flush = time.time()
    collection.flush()
    end_flush = time.time()
    print(f"Succeed in {round(end_flush - start_flush, 4)} seconds!")
    # build index
    index_params = {
        "index_type": "AUTOINDEX",
        "metric_type": "L2",
        "params": {}}
    t0 = time.time()
    print("Building AutoIndex...")
    collection.create_index(
        field_name=book_intro_field.name,
        index_params=index_params)
    t1 = time.time()
    print(f"Succeed in {round(t1 - t0, 4)} seconds!")

    # load collection
    t0 = time.time()
    print("Loading collection...")
    collection.load()
    t1 = time.time()
    print(f"Succeed in {round(t1 - t0, 4)} seconds!")


    # 定义异步执行搜索的任务

    def perform_searches():
        # 创建一个任务列表
        tasks = []
        nq = 1
        topk = 1
        search_params = {"metric_type": "L2", "params": {"level": 2}}

        # 创建 1000 个搜索任务
        for i in range(10000):
            print(f"Creating search task {i}...")
            search_vec = [[random.random() for _ in range(dim)]
                          for _ in range(nq)]
            tasks.append(
                collection.search(search_vec,
                                  anns_field=book_intro_field.name,
                                  param=search_params,
                                  limit=topk,
                                  guarantee_timestamp=1,
                                  _async=True))
        results = [task.result() for task in tasks]
        # 等待所有搜索任务完成
        return results


    # 运行异步搜索任务
    start_time = time.time()
    search_results = perform_searches()
    end_time = time.time()

    # 输出搜索结果和总耗时
    for i, result in enumerate(search_results):
        print(f"Result for search {i}: {result}")

    print(f"Total search time: {round(end_time - start_time, 4)} seconds")
    # average time
    print(f"Average search time: {round((end_time - start_time) / 1000, 4)} seconds")

    connections.disconnect("default")

# 10，000 次搜索结果：
# Total search time: 25.8313 seconds
# Average search time: 0.0258 seconds
