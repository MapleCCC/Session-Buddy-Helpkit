"""
If the purpose of freezing list or dict is just want to get a hash digest,
then use `hash_list` and `hash_dict` directly instead of use `hash(freeze_list(l))`
or `hash(freeze_dict(d))`. They are faster and more space efficient by using the technique
of lazy evaluation over a stream of input data, without the need to construct a whole large
object in the memory, which could be both time costly and space costly.

Note that hash value produced by `hash_list` and `hash_dict` are not stable. Don't expect to
get identical value in different versions of Python interpreter, or even different run of the
same interpreter.

If you want stable and persistent hash result, try `hashlib`.
"""

import itertools
from typing import *

from .pyobjhash import *


__all__ = ["freeze", "ihash"]

# sentinel pattern
# these objects are immutable global singletons within a session of Python interpreter
# which implies that you should not account on them to produce some stable
# and reproducible data that can persists across different instances of Python interpreters.
# If you want to have persisitent hash result, try hashlib.
list_sentinel = object()
dict_sentinel = object()

# hashable implies immutable. Immutable is a form of freeze
Immutable = Hashable


def freeze(item) -> Immutable:
    if isinstance(item, Hashable):
        # WARNING: A great gotchar here is that passing isinstance(x, Hashable) test
        # doesn't necessarily imply that hash(x) won't fail.
        # An example is that some tuples contain elements that are unhashable, despite
        # they passing isinstance(x, Hashable) test.
        if isinstance(item, tuple):
            return freeze_list(item)
        try:
            hash(item)
        except TypeError:
            raise ValueError(f"Cannot freeze")
        return item
    elif isinstance(item, list):
        return freeze_list(item)
    elif isinstance(item, dict):
        return freeze_dict(item)
    else:
        raise ValueError(f"Cannot freeze unsupported type {type(item)}")


def ihash(item) -> int:
    """
    ihash is a drop-in replacement for Python's builtin hash function.
    It is able to hash a broader range of objects.
    """
    if isinstance(item, Hashable):
        # WARNING: A great gotchar here is that passing isinstance(x, Hashable) test
        # doesn't necessarily imply that hash(x) won't fail.
        # An example is that some tuples contain elements that are unhashable, despite
        # they passing isinstance(x, Hashable) test.
        if isinstance(item, tuple):
            return hash_list(item)
        try:
            return hash(item)
        except TypeError:
            raise TypeError("Unhashable")
    elif isinstance(item, list):
        return hash_list(item)
    elif isinstance(item, dict):
        return hash_dict(item)
    else:
        raise TypeError(f"Unhashable type {type(item)}")


# add sentinel to mixup the result
def freeze_list(l: List) -> FrozenSet:
    """
    This function provides a one-to-one mapping from a list instance
    to a frozenset instance. The mapped frozenset is guaranteed to contain only hashable
    elements, hence the frozenset itself becomes hashable and immutable.

    Highly likely no two different lists are mapped to a same frozenset.
    Two eqaul lists always yield the same frozenset. That is, the following property
    always holds: x == y -> hash(x) == hash(y)

    If the mapping cannot be found for some lists, a ValueError will be raised.

    Despite the name, argument other than list is also acceptable as input.
    Any finite iterable also works.

    Known hash collisions are:
        False and "" and 0
        -1 and -2 and -1.0 and -2.0
    """

    def helper(l: List) -> Generator:
        yield list_sentinel
        for i, item in enumerate(l):
            yield (freeze(item), i)

    return frozenset(helper(l))


# add sentinel to mix up the result
def freeze_dict(d: Dict) -> FrozenSet:
    """
    This function provides a one-to-one mapping from a dict instance
    to a frozenset instance. The mapped frozenset is guaranteed to contain only hashable
    elements, hence the frozenset itself becomes hashable and immutable.

    Highly likely no two different dicts are mapped to a same frozenset.
    Two eqaul dicts always yield the same frozenset. That is, the following property
    always holds: x == y -> hash(x) == hash(y)

    If the mapping cannot be found for some dicts, a ValueError will be raised.

    Despite the name, argument other than list is also acceptable as input.
    Any finite iterable also works.

    Known hash collisions are:
        False and "" and 0
        -1 and -2 and -1.0 and -2.0
    """
    return frozenset(map(freeze, d.items())) | {dict_sentinel}


def freeze_dict_using_tuple_method(d: Dict) -> Tuple:
    return (dict_sentinel,) + tuple(map(freeze, sorted(d.items())))


def hash_list(l: List) -> int:
    def helper(l: List) -> Generator:
        yield hash(list_sentinel)
        for i, item in enumerate(l):
            yield hash_tuple_from_hashes_of_elements((ihash(item), hash(i)))

    return hash_frozenset_from_hashes_of_elements(helper(l))


def hash_dict(d: Dict) -> int:
    return hash_frozenset_from_hashes_of_elements(
        itertools.chain(map(ihash, d.items()), (hash(dict_sentinel),))
    )
