"""
If the purpose of freezing list or dict is just want to get a hash digest,
then use `hash_list` and `hash_dict` directly instead of use `hash(freeze_list(l))`
or `hash(freeze_dict(d))`. They are faster and more space efficient by using the technique of
lazy evaluation without the need to construct a whole large object in the memory, which could
be both time costly and space costly.
"""

from typing import *
from .pyobjhash import *
import itertools

__all__ = ["freeze", "ihash"]

list_sentinel = object()
dict_sentinel = object()


def freeze(item) -> Hashable:
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


# TODO: Do we want to have no two different lists mapping to a same tuple,
# or do we want to have no two different objects mapping to a same tuple.
# if the latter if true, we need to add some sentinel to mixup the hash
def freeze_list(l: List) -> FrozenSet:
    """
    This function provides a one-to-one mapping from a list instance
    to a tuple instance. The mapped tuple is guaranteed to contain only hashable
    elements, hence the tuple itself becomes hashable.

    Highly likely no two different lists are mapped to a same tuple.
    Two eqaul lists yield the same tuple.

    If the mapping cannot be found for some lists, a ValueError will be raised.
    """

    def helper(l: List) -> Generator:
        yield list_sentinel
        for i, item in enumerate(l):
            yield (freeze(item), i)

    return frozenset(helper(l))


def freeze_dict(d: Dict) -> FrozenSet:
    """
    This function provides a one-to-one mapping from a dict instance
    to a tuple instance. The mapped tuple is guaranteed to contain only hashable
    elements, hence the tuple itself becomes hashable.

    Highly likely no two different dicts are mapped to a same tuple.
    Two eqaul dicts yield the same tuple.

    If the mapping cannot be found for some dicts, a ValueError will be raised.

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
