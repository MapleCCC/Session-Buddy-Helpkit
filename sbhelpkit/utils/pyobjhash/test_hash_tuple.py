import sys
from typing import *

from hypothesis import given, settings, assume
from hypothesis.strategies import *

from .hash_tuple import *

if sys.version_info < (3, 7):
    raise RuntimeError("Do not test under v3.7.0. "
        "We need built-in hash implementation up to v3.7.0 to test against.")

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
acceptable_collision_rate_threshold = 0.03
total_test_case = 500
min_distinct_test_case = 300
seen_test_cases = set()


@settings(max_examples=total_test_case)
@given(lists(hashable_types), lists(hashable_types))
def test_hash_different_list_low_collision_rate_helper(
    l1: List[Hashable], l2: List[Hashable]
) -> None:
    t1, t2 = tuple(l1), tuple(l2)
    assume(t1 != t2)
    assume({t1, t2} not in seen_test_cases)
    seen_test_cases.add(frozenset({t1, t2}))

    global collision_count
    if hash_tuple(t1) == hash_tuple(t2):
        collision_count += 1


@given(just(None))
def test_hash_different_list_low_collision_rate(_: None) -> None:
    assert len(seen_test_cases) > min_distinct_test_case
    assert (
        collision_count / len(seen_test_cases)
    ) < acceptable_collision_rate_threshold
