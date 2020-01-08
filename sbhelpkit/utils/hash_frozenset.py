from ctypes import *
from typing import *
from functools import reduce
import pdb


# Reference: https://github.com/python/cpython/blob/4171b8e41165daadb034867eae61e05f8d2bc9c0/Include/pyport.h#L91
Py_hash_t = c_ssize_t
Py_uhash_t = c_size_t

Py_ssize_t = c_ssize_t


# Reference: https://github.com/python/cpython/tree/v3.7.0/Objects/setobject.c#L764
# Note that frozenset caches hash value internally. So sometimes it may be faster to just query.
def hash_frozenset(fs: FrozenSet) -> int:
    return hash_frozenset_from_elements(fs)


def hash_frozenset_from_elements(elements: Iterable) -> int:
    def _shuffule_bits(h: Py_uhash_t) -> Py_uhash_t:
        # For increase the bit dispersion for closely spaced hash values.
        # Reference: https://github.com/python/cpython/blob/676b16c14040ddb9a2ef3408e66a77c1dfb8e841/Objects/setobject.c#L747
        return Py_uhash_t(((h.value ^ 89869747) ^ (h.value << 16)) * 3644798167)

    def reducer(state: Tuple[Py_uhash_t, int], y: Py_uhash_t) -> Tuple[Py_uhash_t, int]:
        acc, counter = state
        return xor(acc, y), counter + 1

    def xor(x: Py_uhash_t, y: Py_uhash_t) -> Py_uhash_t:
        return Py_uhash_t(x.value ^ y.value)

    hashes = (Py_hash_t(hash(e)) for e in elements)
    dispersed_hashes = map(_shuffule_bits, hashes)
    h, count = reduce(reducer, dispersed_hashes, (Py_uhash_t(0), 0))

    h.value ^= (Py_uhash_t(count).value + 1) * 1927868237

    # disperse in case of nested frozensets
    h.value ^= (h.value >> 11) ^ (
        h.value >> 25
    )  # CPython 3.6.4 and 3.7.0 have difference in this line
    h.value = h.value * 69069 + 907133923

    # Reserve -1 as error code, although this should not matter in Python level.
    if h.value == Py_uhash_t(-1):
        h.value = 590923713

    return Py_hash_t(h.value).value
