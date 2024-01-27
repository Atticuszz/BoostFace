import multiprocessing
import queue
import uuid
from time import sleep
from timeit import default_timer
from typing import Any

import numpy as np
from line_profiler_pycharm import profile

from src.boostface.app.common import LightImage
from src.boostface.app.detector import Detector


# Define the function to generate a single image


def generate_light_image(pixels=5000000):
    """
    Generate a LightImage object with approximately the specified number of pixels.
    Assume a 3-channel image (RGB).
    """
    # Assuming a square image for simplicity: sqrt(5000000) is approximately 2236.07
    # So we use 2236 for both width and height to approximate 5000000 pixels for the 3 channels
    side_length = int(np.sqrt(pixels / 3))
    image_array = np.random.randint(0, 256, (side_length, side_length, 3), dtype=np.uint8)
    return LightImage(nd_arr=image_array)


@profile
def sender(imgs: list[np.ndarray],
           task_queue: multiprocessing.Queue,
           result_dict: dict,
           cost_time: dict):
    def add_task(
            task: Any,
            task_queue: multiprocessing.Queue,
            cost_time: dict,
            timeout: int = 5):
        try:
            start_time = default_timer()
            task_id = uuid.uuid4()
            task_queue.put((task_id, task), timeout=timeout)
            elapsed_time = default_timer() - start_time
            cost_time['add_task'].append(default_timer() - start_time)
            print(f"Task added: ID={task_id}, Time={elapsed_time}")
            return task_id
        except queue.Full:
            raise queue.Full("The task queue is full. Try again later.")

    def get_result(
            task_id: uuid.UUID,
            result_dict: dict,
            cost_time: dict,
            timeout=10):
        # Function to get the result of a task with timing
        start_time = default_timer()
        while True:
            if task_id in result_dict:
                result = result_dict.pop(task_id)
                elapsed_time = default_timer() - start_time
                cost_time['get_result'].append(elapsed_time)
                print(f"Task completed: ID={task_id}, Time={elapsed_time}")
                return task_id, result
            elif default_timer() - start_time > timeout:
                raise queue.Empty(
                    f"Timeout while waiting for the result of task {task_id}")
            sleep(0.01)

    print("add_task process")
    for img in imgs:
        task_id = add_task(img, task_queue, cost_time)
        results = get_result(task_id, result_dict, cost_time)
        # 模拟消费
        print(f"Task for image with task ID {task_id} added to the queue.")
    # Add a None task to signal the end of the queue
    add_task(None, task_queue, cost_time)


@profile
# Function to be run by worker processes
def worker(task_queue: multiprocessing.Queue,
           result_dict: dict):
    print("worker process")
    detector = Detector()
    while True:
        try:
            # 模拟消费task并且产生结果
            task_id, img = task_queue.get(timeout=5)
            if img is None:
                print("Received None task, exiting.")
                break
            detector(img)
            # Process the task (in this case, we'll just set the result to True
            # to simulate success)
            result_dict[task_id] = True
        except queue.Empty:
            print("No task received in the last second.")
            break


if __name__ == '__main__':
    # 创建一个管理器
    with multiprocessing.Manager() as manager:
        task_queue = manager.Queue()
        result_dict = manager.dict()
        cost_time = manager.dict(get_result=[], add_task=[])
        print("main process")
        # Add tasks to the queue
        num_images = 500  # Number of images to generate and add to the queue
        imgs = [generate_light_image() for _ in range(num_images)]
        print(f"Generated {num_images} images.")
        # 开启两个进程，一个发送任务，一个接收结果
        user = multiprocessing.Process(
            target=sender, args=(
                imgs, task_queue, result_dict, cost_time,))
        receiver = multiprocessing.Process(
            target=worker, args=(
                task_queue, result_dict,))
        receiver.start()
        user.start()

        user.join()
        receiver.join()
        print("All tasks complete.")
