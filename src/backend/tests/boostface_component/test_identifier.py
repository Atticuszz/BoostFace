# coding=utf-8
import concurrent
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

import numpy as np
from line_profiler_pycharm import profile
from matplotlib import pyplot as plt
from scipy.stats import linregress

from app.services.inference.common import IdentifyManager, Image2Detect
from src.boostface.component.identifier import IdentifyWorker, Identifier
from tests import generate_image2detect


@profile
def process_image(
        images: list[Image2Detect],
        identifier_manager: IdentifyManager):
    """
    thread of process_image
    :param images:
    :param identifier_manager:
    :return:
    """
    elapsed = []
    for image in images:
        start = default_timer()
        identifier = Identifier(identifier_manager)
        res = identifier.identified_results(image)
        print("res:", res, "cost:", default_timer() - start)
        elapsed.append(default_timer() - start)
    return elapsed


def plot_mean_times_with_trend(mean_times):
    # Define the x values (number of threads)
    x_values = range(1, len(mean_times) + 1)

    # Compute the linear regression to get the slope and intercept
    slope, intercept, r_value, p_value, std_err = linregress(
        x_values, mean_times)

    # Create a trendline using the slope and intercept
    trendline = [slope * i + intercept for i in x_values]

    # Plotting the original mean elapsed times with data points
    plt.figure(figsize=(10, 6))
    plt.plot(
        x_values,
        mean_times,
        marker='o',
        label='Mean Elapsed Time',
        linestyle='-',
        color='blue')

    # Plotting the trend line
    plt.plot(
        x_values,
        trendline,
        label=f'Trendline (slope: {slope:.4f})',
        linestyle='--',
        color='red')

    # Annotating the slope on the plot
    plt.text(
        0.6 *
        max(x_values),
        intercept +
        slope *
        0.6 *
        max(x_values),
        f'Slope: {slope:.4f}',
        fontsize=12,
        color='red')

    # Highlighting the data points and showing (x, y) values
    for i, txt in enumerate(mean_times):
        plt.annotate(
            f'({i + 1}, {txt:.4f})',
            (i + 1,
             txt),
            textcoords="offset points",
            xytext=(
                0,
                10),
            ha='center')

    plt.xlabel('Number of Threads')
    plt.ylabel('Mean Elapsed Time (s)')
    plt.title('Mean Elapsed Time vs. Number of Threads with Trendline')
    plt.legend()
    plt.grid(True)
    plt.show()


def test_IdentifyWorker():
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
            print("created sub process")

            # 创建虚拟数据
            fake_img: list[Image2Detect] = [
                generate_image2detect(
                    size=(
                        640, 640)) for _ in range(50)]
            for num_threads in range(1, 2):  # from 1 to 20 threads
                print(f"Testing {num_threads} threads")
                # 使用线程池处理图像
                elapsed_time = []
                # 模拟5个线程同时喂给处理进程
                with ThreadPoolExecutor(max_workers=num_threads) as executor:

                    futures = [
                        executor.submit(
                            process_image,
                            fake_img,
                            identifier_manager) for _ in range(num_threads)]
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
