import time

from source import DEBUG


def check_perfo(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print_debug(f"Execution time for {func.__name__}: {end_time - start_time} seconds")
        return result
    return wrapper


def print_debug(txt):
    if DEBUG:
        print(f"[DEBUG] {txt}")

