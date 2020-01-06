from collections import namedtuple
from ctypes import *
from functools import reduce
from typing import *

# Reference: https://github.com/python/cpython/blob/4171b8e41165daadb034867eae61e05f8d2bc9c0/Include/pyport.h#L91
Py_hash_t = c_ssize_t
Py_uhash_t = c_size_t

Py_ssize_t = c_ssize_t

# Porting tuplehash CPython v3.6.0 implementation from C layer to Python layer.
# Reference: https://github.com/python/cpython/blob/4171b8e41165daadb034867eae61e05f8d2bc9c0/Objects/tupleobject.c#L344
def hash_tuple(t: Tuple) -> int:
    acc = Py_uhash_t(0x345678)
    length = Py_ssize_t(len(t))
    mult = Py_uhash_t(0xF4243)

    for i, item in enumerate(t):
        try:
            h = Py_hash_t(hash(item))
        except TypeError:
            raise TypeError("Unhashable tuple")
        acc.value = (acc.value ^ h.value) * mult.value
        mult.value += Py_hash_t(
            82520 + length.value - i - 1 + length.value - i - 1
        ).value

    acc.value += 97531
    if acc.value == Py_uhash_t(-1).value:
        acc.value = -2
    return Py_hash_t(acc.value).value


def hash_tuple_from_stream_of_tuple_elements(elements: Iterable) -> int:
    def consume(
        state: Tuple[Py_uhash_t, Py_uhash_t, int], element_hash: Py_hash_t
    ) -> Tuple[Py_uhash_t, Py_uhash_t, int]:
        acc, mult, counter = state
        acc.value = (acc.value ^ element_hash.value) * mult.value
        mult.value += Py_hash_t(
            82520 + length.value + length.value - 2 * counter - 2
        ).value
        counter += 1
        return acc, mult, counter

    try:
        element_hashes = [Py_hash_t(hash(e)) for e in elements]
    except TypeError:
        raise TypeError("Unhashable tuple")

    length = Py_ssize_t(len(element_hashes))
    initial_state = (Py_uhash_t(0x345678), Py_uhash_t(0xF4243), 0)

    acc, _, _ = reduce(consume, element_hashes, initial_state)

    acc.value += 97531
    if acc.value == Py_uhash_t(-1).value:
        acc.value = -2
    return Py_hash_t(acc.value).value


if __name__ == "__main__":
    hash_tuple((0,))
