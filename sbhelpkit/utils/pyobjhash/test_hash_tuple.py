from typing import *

from hypothesis import given
from hypothesis.strategies import *

from .hash_tuple import *

hashable_types = none() | booleans() | floats() | text()


@given(lists(hashable_types))
def test_hash_tuple_compliance(l: List) -> None:
    t = tuple(l)
    assert hash_tuple(t) == hash(t)


@given(lists(hashable_types))
def test_hash_tuple_from_stream_of_tuple_elements(l: List) -> None:
    itr = iter(tuple(l))
    assert hash_tuple_from_stream_of_tuple_elements(itr) == hash(itr)


@given(lists(hashable_types))
def test_tuplehasher(l: List) -> None:
    t = tuple(l)
    th = TupleHasher(len(t))
    for element in t:
        th.update(element)
    assert th.digest() == hash(t)
