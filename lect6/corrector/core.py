import itertools
from collections.abc import Callable
from functools import reduce


def pipe(*funcs) -> Callable:
    return lambda x: reduce(lambda value, a: a(value), funcs, x)

def pipe(*funcs) -> Callable:
    return lambda x: reduce(lambda value, a: a(value), funcs, x)
def compose(*funcs):
    return pipe(*reversed(funcs))

def take(n: int, iterable):
    if n <= 0:
        return []
    for i, x in iterable:
        yield x
        if i>=n:
            return

print(list(take(5, [1,2,3,4,5,6,7,8,9,10])))
print(list(take(5, [1,2,3,4,5,6,7,8,9,10])))