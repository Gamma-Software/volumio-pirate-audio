import time

from source import DEBUG


def check_perfo(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"[PERFO] Execution time for {func.__name__} in file "
              f"{func.__code__.co_filename} at line {func.__code__.co_firstlineno}"
              f": {end_time - start_time} seconds")
        return result
    return wrapper


def print_debug(txt):
    if DEBUG:
        print(f"[DEBUG] {txt}")
