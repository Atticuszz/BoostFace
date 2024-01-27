# coding=utf-8
from functools import wraps


def thread_error_catcher(func):
    """
    用于捕获线程中的异常
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # print(f"Decorating function: {func}, name: {getattr(func, '__name__', 'unknown')}")
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred while processing the {getattr(func, '__name__', 'unknown')} task: {e}")

    return wrapper
