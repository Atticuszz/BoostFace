import os
from multiprocessing import Process, Queue, Event
from queue import Empty
from time import sleep
from timeit import default_timer as timer

import numpy as np
from line_profiler import profile

from src.boostface.app.common import LightImage
from src.boostface.app.identifier import Extractor


# 假设的模拟数据生成函数
def generate_fake_data():
    img_data = np.random.randint(0, 256, (640, 640, 3), dtype=np.uint8)
    bbox = np.array([[0, 0], [640, 0], [640, 640], [0, 640]])
    kps = np.random.randint(0, 640, (5, 2))
    det_score = np.random.random()
    return LightImage(nd_arr=img_data), bbox, kps, det_score


stop_event = Event()


# 工作进程的函数

@profile
def worker(queue, performance_log):
    extractor = Extractor()
    while not stop_event.is_set():
        try:
            item = queue.get(timeout=1)  # 设置超时时间
            if item is None:  # 检测到哨兵值，退出循环
                break
            img2extract, bbox, kps, det_score = item

            start_time = timer()
            embedding = extractor(img2extract, bbox, kps, det_score)
            end_time = timer()
            duration = end_time - start_time
            performance_log.put((os.getpid(), start_time, end_time, duration))
            print(
                f"Processed data, embedding shape: {embedding.shape}, duration: {duration:.4f} seconds")
        except Empty:
            # 队列超时，但是没有其它错误，忽略并继续检查停止事件
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break


# 创建并启动数据生成进程

@profile
def data_generator(queue):
    while not stop_event.is_set():
        try:
            data = generate_fake_data()
            queue.put(data, timeout=5)
        except queue.Fuil:
            # 队列超时，但是没有其它错误，忽略并继续检查停止事件
            continue


# 主函数


def main():
    num_workers = 1
    queue = Queue(maxsize=1000)  # 队列最大容量
    performance_log = Queue()  # 性能日志队列

    producer = Process(tar
    get = data_generator, args = (queue,))
    producer.start()
    print("Producer started.")
    # 创建并启动工作进程
    workers = []
    for _ in range(num_workers):
        p = Process(target=worker, args=(queue, performance_log))
        p.start()
        workers.append(p)

    # 运行测试一段时间后关闭
    sleep(60)  # 运行60秒

    stop_event.set()  # 设置停止事件
    # 向队列中加入等同于工作进程数量的哨兵值，以通知它们停止
    for _ in range(num_workers):
        queue.put(None)
    print("Stopping workers...")
    producer.terminate()  # 关闭数据生成进程
    print("Producer terminate.")
    producer.join()
    print("Producer joined.")

    # 等待所有工作进程完成
    for p in workers:
        p.terminate()
        p.join()
    print("Workers joined.")
    # 在主进程中，测试完成后
    total_duration = 0
    total_items = 0

    # 收集性能日志
    while not performance_log.empty():
        pid, start, end, duration = performance_log.get()
        total_duration += duration
        total_items += 1
        print(f"Worker {pid}: Duration {duration:.4f} seconds")

    if total_items > 0:
        average_time = total_duration / total_items
        print(f"Average processing time per item: {average_time:.4f} seconds")
        print(
            f"Throughput: {total_items / total_duration:.2f} items per second")


if __name__ == "__main__":
    main()

# cpu 上面，一个cpu一个onnxrunner就够了
