import datetime
import time
import traceback
from contextlib import contextmanager
from functools import wraps
from timeit import default_timer

import requests

from src.app.config import qt_logger


def error_handler(f):
    """ decorator to catch error and print error info"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        """ wrapper to catch error and print error info"""
        try:
            return f(*args, **kwargs)
        except requests.HTTPError:
            error_info = traceback.format_exc()
            qt_logger.error(f"HTTPError at {f.__name__}  with {error_info}")
        except Exception:
            error_info = traceback.format_exc()
            qt_logger.error(f"Error at {f.__name__} with {error_info}")
        return None

    return wrapper


@contextmanager
def calm_down(min_time: float):
    """
    上下文管理器，确保代码块执行的最小时间。
    :param min_time: 稳定时间（秒）
    """
    start_time = default_timer()
    try:
        yield
    finally:
        end_time = default_timer()
        elapsed_time = end_time - start_time
        if elapsed_time < min_time:
            time.sleep(min_time - elapsed_time)
