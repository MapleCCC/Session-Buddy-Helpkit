from typing import *

from hypothesis import given
from hypothesis.strategies import *

from tuplehash import *

# TODO: try testing on tuple with heterogeneous typed elements.


@given(lists(integers()))
def test_hash_tuple_compliance(l: List[int]) -> None:
    t = tuple(l)
    assert hash_tuple(t) == hash(t)


@given(lists(integers()))
def test_hash_tuple_from_stream_of_tuple_elements(l: List) -> None:
    t = tuple(l)
    assert hash_tuple_from_stream_of_tuple_elements(t) == hash(t)


@given(lists(integers()))
def test_tuplehasher(l: List[int]) -> None:
    t = tuple(l)
    th = TupleHasher(len(t))
    for element in t:
        th.update(element)
    assert th.digest() == hash(t)
