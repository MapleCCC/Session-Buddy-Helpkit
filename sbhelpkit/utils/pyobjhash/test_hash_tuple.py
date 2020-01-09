from typing import *

from hypothesis import given, settings, assume
from hypothesis.strategies import *

from .hash_tuple import *

hashable_types = none() | booleans() | floats() | text()


@given(lists(hashable_types))
def test_hash_tuple_compliance(l: List) -> None:
    t = tuple(l)
    assert hash_tuple(t) == hash(t)


@given(lists(hashable_types))
def test_hash_tuple_from_stream_of_tuple_elements(l: List) -> None:
    t = tuple(l)
    assert hash_tuple_from_stream_of_tuple_elements(iter(t)) == hash(tuple(t))


@given(lists(hashable_types))
def test_tuplehasher(l: List) -> None:
    t = tuple(l)
    th = TupleHasher(len(t))
    for element in t:
        th.update(element)
    assert th.digest() == hash(t)


# It's hard to instruct hypothesis to generate a sufficient amount of pair of unequal lists.
# So we are gonna use a trick here.
# Use helper function to exploit hypothesis' search strategies.
# Use global variable to track intermediate information.

collision_count = 0
total_count = 0
acceptable_collision_rate_threshold = 0.03
total_test_case = 500
min_test_case = 300

@settings(max_examples=total_test_case)
@given(lists(hashable_types), lists(hashable_types))
def test_hash_different_list_low_collision_rate_helper(
    l1: List[Hashable], l2: List[Hashable]
) -> None:
    global collision_count, total_count
    assume(l1 != l2)
    t1, t2 = tuple(l1), tuple(l2)
    if hash_tuple(t1) == hash_tuple(t2):
        collision_count += 1
    total_count += 1


@given(just(None))
def test_hash_different_list_low_collision_rate(_: None) -> None:
    assert total_count >= min_test_case
    assert (collision_count / total_count) < acceptable_collision_rate_threshold
