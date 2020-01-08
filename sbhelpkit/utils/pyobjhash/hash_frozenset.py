from ctypes import *
from functools import reduce
from typing import *

__all__ = ["hash_frozenset", "hash_frozenset_from_elements"]

Py_ssize_t = c_ssize_t

# Reference: https://github.com/python/cpython/blob/v3.7.0/Include/pyport.h#L91
Py_hash_t = Py_ssize_t
Py_uhash_t = c_size_t


# Reference: https://github.com/python/cpython/blob/v3.7.0/Objects/setobject.c#L764
# Note that frozenset caches hash value internally. So sometimes it may be faster to just query.
def hash_frozenset(fs: FrozenSet) -> int:
    return hash_frozenset_from_elements(fs)


def hash_frozenset_from_elements(elements: Iterable) -> int:
    def _shuffule_bits(h: Py_uhash_t) -> Py_uhash_t:
        # For increase the bit dispersion for closely spaced hash values.
        # Reference: https://github.com/python/cpython/blob/v3.7.0/Objects/setobject.c#L752
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
