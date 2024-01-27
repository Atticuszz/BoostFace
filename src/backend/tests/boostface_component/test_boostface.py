# coding=utf-8
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from src.boostface.app import boostface
from app.services.inference.common import IdentifyManager
from src.boostface.component.identifier import IdentifyWorker

if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        print("main process start")

        identifier_task_queue = manager.Queue(maxsize=100)
        identifier_result_dict = manager.dict()
        identifier_manager = IdentifyManager(
            identifier_task_queue, identifier_result_dict)
        print("created identifier_manager")

        worker = IdentifyWorker(identifier_task_queue, identifier_result_dict)
        mean_elapsed_times = []
        threads_num = 5
        try:
            worker.start()
            print("created sub process")
            with ThreadPoolExecutor() as executor:
                # sleep(10)
                if_done = Event()
                [executor.submit(boostface, identifier_manager, if_done) for _ in range(threads_num)]

                executor.shutdown(wait=True)
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
        finally:
            worker.stop()
