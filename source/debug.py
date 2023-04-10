import sys
import time

from source import DEBUG


def check_perfo(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"[PERFO] {time.asctime()} Execution time for {func.__name__} in file "
              f"{func.__code__.co_filename} at line {func.__code__.co_firstlineno}"
              f": {end_time - start_time} seconds")
        return result
    return wrapper


def sizeof_fmt(num, suffix='B'):
    ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def print_memory_usage():
    for name, size in sorted(((name, sys.getsizeof(value)) for name, value in list(
                            locals().items())), key=lambda x: -x[1])[:10]:
        print("{:>30}: {:>8}".format(name, sizeof_fmt(size)))


def print_debug(txt):
    if DEBUG:
        print(f"[DEBUG] {txt}")
