import concurrent
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from app.services.inference.common import IdentifyManager, Face2Search
from src.boostface.component.identifier import IdentifyWorker
from tests import generate_face2search


def thread_work(images: list[Face2Search], identifier_manager: IdentifyManager):
    elapsed = []
    for image in images:
        start = default_timer()
        uuid = identifier_manager.add_task(image)
        result = identifier_manager.get_result(uuid)
        print("task:", uuid, "result:", result, "cost:", default_timer() - start)
        elapsed.append(default_timer() - start)
        # print("task:", uuid, "result:", result)
    return elapsed


def register_face():
    with multiprocessing.Manager() as manager:
        print("main process start")

        identifier_task_queue = manager.Queue(maxsize=100)
        identifier_result_dict = manager.dict()
        identifier_manager = IdentifyManager(
            identifier_task_queue, identifier_result_dict)
        print("created identifier_manager")

        worker = IdentifyWorker(identifier_task_queue, identifier_result_dict)
        mean_elapsed_times = []
        try:
            worker.start()
            # process are running now

            print("created sub process")

            # 创建虚拟数据
            fake_img = [generate_face2search(size=(640, 640)) for _ in range(50)]
            for num_threads in range(1, 6):  # from 1 to 20 threads
                print(f"Testing {num_threads} threads")
                # 使用线程池处理图像
                elapsed_time = []
                # 模拟5个线程同时喂给处理进程
                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    futures = [executor.submit(process_image, fake_img, identifier_manager) for _ in range(num_threads)]
                    for future in concurrent.futures.as_completed(futures):
                        elapsed = future.result()
                        elapsed_time.append(np.mean(elapsed))
                mean_elapsed_times.append(np.mean(elapsed_time))

        except KeyboardInterrupt:
            print("KeyboardInterrupt")
        finally:
            worker.stop()
            #             打印图表
            plot_mean_times_with_trend(mean_elapsed_times)


if __name__ == '__main__':
    # pass
    test_IdentifyWorker()
