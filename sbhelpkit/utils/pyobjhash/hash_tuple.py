from collections import namedtuple
from ctypes import *
from functools import reduce
from typing import *

__all__ = [
    "hash_tuple",
    "hash_tuple_from_stream_of_tuple_elements",
    "hash_tuple_from_hashes_of_elements",
    "TupleHasher",
]

Py_ssize_t = c_ssize_t

# Reference: https://github.com/python/cpython/blob/v3.7.0/Include/pyport.h#L91
Py_hash_t = Py_ssize_t
Py_uhash_t = c_size_t


# TODO: try v3.8.0 implementation
# Porting tuplehash CPython v3.6.0 implementation from C layer to Python layer.
# ctypes are used to simulate overflow behaviour.
# Is it possible to simulate the overflow behaviour using mere Pythonic constructs, without using ctypes?
# Reference: https://github.com/python/cpython/blob/v3.7.0/Objects/tupleobject.c#L348
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
        delta = Py_ssize_t(length.value - i - 1)
        mult.value += Py_hash_t(82520 + delta.value + delta.value).value

    acc.value += 97531
    if acc.value == Py_uhash_t(-1).value:
        acc.value = -2
    return Py_hash_t(acc.value).value


def hash_tuple_from_stream_of_tuple_elements(elements: Iterable) -> int:
    try:
        element_hashes = [hash(e) for e in elements]
    except TypeError:
        raise TypeError("Unhashable tuple")

    return hash_tuple_from_hashes_of_elements(element_hashes)


def hash_tuple_from_hashes_of_elements(element_hashes: List[int]) -> int:
    State = namedtuple("State", ["acc", "mult", "counter"])

    def consume(state: State, element_hash: int) -> State:
        acc, mult, counter = state
        acc.value = (acc.value ^ Py_hash_t(element_hash).value) * mult.value
        delta = Py_ssize_t(length.value - counter - 1)
        mult.value += Py_hash_t(82520 + delta.value + delta.value).value
        counter += 1
        return acc, mult, counter

    length = Py_ssize_t(len(element_hashes))
    initial_state = State(acc=Py_uhash_t(0x345678), mult=Py_uhash_t(0xF4243), counter=0)

    acc, _, _ = reduce(consume, element_hashes, initial_state)

    acc.value += 97531
    if acc.value == Py_uhash_t(-1).value:
        acc.value = -2
    return Py_hash_t(acc.value).value


class TupleHasher:
    def __init__(self, length: int) -> None:
        self.acc = Py_uhash_t(0x345678)
        self.mult = Py_uhash_t(0xF4243)
        self.counter = 0
        self.len = Py_ssize_t(length)

    def update(self, data) -> None:
        try:
            h = Py_hash_t(hash(data))
        except TypeError:
            raise TypeError("Unhashable tuple")
        self.acc.value = (self.acc.value ^ h.value) * self.mult.value
        delta = Py_ssize_t(self.len.value - self.counter - 1)
        self.mult.value += Py_hash_t(82520 + delta.value + delta.value).value
        self.counter += 1

    def digest(self) -> int:
        # TODO: will modification to acc affect self.acc?
        acc = self.acc
        acc.value += 97531
        if acc.value == Py_uhash_t(-1).value:
            acc.value = -2
        return Py_hash_t(acc.value).value


if __name__ == "__main__":
    hash_tuple((0,))
