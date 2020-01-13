import builtins
import itertools
import functools

from typing import *

__all__ = ["disable_lazy_feature"]

# much better is to inspect the AST, and figure out if the iterator
# is not being used by next(), hence safe to coerce to list().

targets_builtins = (
    "enumerate",
    "filter",
    # "iter", # in case user want to use next() on iterator returned by iter(), which is not uncommon pattern.
    "map",
    "range",
    "reversed",
    "zip",
)

targets_itertools = (
    "accumulate",
    "chain",
    "combinations",
    "combinations_with_replacement",
    "compress",
    "count",
    "cycle",
    "dropwhile",
    "filterfalse",
    "groupby",
    "islice",
    "permutations",
    "product",
    "repeat",
    "starmap",
    "takewhile",
    "tee",
    "zip_longest",
)


def nonlazify(func: Callable) -> Callable:
    assert isinstance(func, Callable)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, Iterator):
            return list(result)
        return result

    return wrapper


def disable_lazy_feature():
    for target in targets_builtins:
        builtins.__dict__[target] = nonlazify(builtins.__dict__[target])

    for target in targets_itertools:
        itertools.__dict__[target] = nonlazify(itertools.__dict__[target])
