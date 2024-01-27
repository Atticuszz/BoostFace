"""
-*- coding: utf-8 -*-
@Organization : SupaVision
@Author       : 18317
@Date Created : 15/12/2023
@Description  :
"""
import itertools
import re
from functools import wraps
from types import FunctionType
from typing import Callable

import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

from timeit import default_timer as timer, default_timer
from pathlib import Path
from contextlib import contextmanager

from matplotlib.colors import TABLEAU_COLORS

from src.app.config import qt_logger

# TODO: add decorator func
# TODO: add fixed time test
# TODO: add resource monitor as single multi tests


class TimeTracker:
    _instance = None

    def __init__(self, base_path):
        pass

    def __new__(cls, base_path):
        if cls._instance is None:
            cls._instance = super(TimeTracker, cls).__new__(cls)
            cls._instance.__init_once(base_path)
        return cls._instance

    def __init_once(self, base_path):
        self.records = {}
        self.start_time = None
        self.base_path = Path(base_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """Call this method to clean up and save the plots."""
        self.save_plots()

    @contextmanager
    def track(self, name):
        """Context manager to track the execution time of a block of code."""
        start = default_timer()
        name = self._sanitize_filename(name)
        if self.start_time is None:
            self.start_time = start  # 记录首次开始时间
        try:
            yield
        finally:
            end = default_timer()
            duration = end - start
            self.records.setdefault(
                name, []).append(
                (start - self.start_time, duration))

    def track_func(self, func: Callable):
        """self.track decorator for functions"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 根据被装饰函数的类型确定如何获取跟踪名称
            if isinstance(func, FunctionType):
                name = func.__qualname__  # 对于类方法和静态方法
            else:
                # 对于实例方法
                name = f"{args[0].__class__.__name__}.{func.__name__}"

            with self.track(name):
                return func(*args, **kwargs)

        return wrapper

    def save_plots(
            self,
            dpi=300,):
        """
        Saves the plots.
        :param combined: If True, plot all records on a single plot. Otherwise, create separate plots.
        :param dpi: The resolution of the plots in dots per inch.
        :param grouped: If True, group the plots by time scale.
        :param time_scale_sec: The time scale in seconds for grouping plots.
        """

        self._save_execution_time_plots(dpi)

    def _save_execution_time_plots(self, dpi):
        output_directory = self.base_path / \
            f"timetracker_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_directory.mkdir(parents=True, exist_ok=True)

        for name, durations in self.records.items():
            plt.figure()
            x, y = zip(*durations)
            plt.plot(x, y, label='Execution Time')

            avg = np.mean(y)
            plt.axhline(
                y=avg,
                color='r',
                linestyle='--',
                label=f'Average: {avg:.4f}s')

            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x, p(x), "r--")

            plt.title(f"Execution Time for '{name}'")
            plt.xlabel('run time')
            plt.ylabel('Time (seconds)')
            plt.legend()
            plt.savefig(output_directory / f"{self._sanitize_filename(name)}.png", dpi=dpi)
            plt.close()

    @staticmethod
    def _sanitize_filename(filename) -> str:
        """
        Removes or replaces characters that are not allowed in a filename.
        """
        # 定义非法字符的模式
        invalid_chars_pattern = r'[<>:"/\\|?*]'

        # 替换所有非法字符为空字符串（或您可以选择替换为其他字符）
        sanitized_filename = re.sub(invalid_chars_pattern, '', filename)

        return sanitized_filename


# Example usage with specified path
output_path = r'C:\Users\18317\python\BoostFace_pyqt6\tests\performance'
time_tracker = TimeTracker(output_path)

if __name__ == '__main__':
    for _ in range(100):
        with time_tracker.track("task1"):
            time.sleep(0.001)
        with time_tracker.track("task2"):
            time.sleep(0.02)
    with time_tracker.track("task2"):
        time.sleep(1)  # Simulate a different task taking 0.5 seconds
    time_tracker.close()
