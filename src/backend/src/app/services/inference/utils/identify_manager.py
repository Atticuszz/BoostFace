import multiprocessing
import queue
import uuid
from time import sleep
from timeit import default_timer
from typing import Any


def add_task(task: Any, task_queue: multiprocessing.Queue, cost_time: dict, timeout: int = 5):
    try:
        start_time = default_timer()
        task_id = uuid.uuid4()
        task_queue.put((task_id, task), timeout=timeout)
        cost_time.setdefault('add_task', []).append(default_timer() - start_time)
        return task_id
    except queue.Full:
        raise queue.Full("The task queue is full. Try again later.")


def get_result(task_id: str, result_dict: dict, cost_time: dict, timeout=10):
    # Function to get the result of a task with timing
    start_time = default_timer()
    while True:
        if task_id in result_dict:
            result = result_dict.pop(task_id)
            elapsed_time = default_timer() - start_time
            cost_time.setdefault('get_result', []).append(elapsed_time)
            return task_id, result
        elif default_timer() - start_time > timeout:
            raise queue.Empty(f"Timeout while waiting for the result of task {task_id}")
        sleep(0.01)
