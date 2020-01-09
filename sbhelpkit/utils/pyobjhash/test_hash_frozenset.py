from typing import *

from hypothesis import given, settings, assume
from hypothesis.strategies import *

from .hash_frozenset import *

hashable_types = none() | booleans() | floats() | text()

# TODO: test on nested frozenset


@given(frozensets(hashable_types))
def test_hash_frozenset_regression(s: FrozenSet) -> None:
    assert hash_frozenset(s) == hash(s)


@given(frozensets(hashable_types))
def test_frozensethasher(s: FrozenSet) -> None:
    sh = FrozenSetHasher()
    for item in s:
        sh.update(item)
    assert sh.digest() == hash(s)


# It's hard to instruct hypothesis to generate a sufficient amount of pair of unequal frozensets.
# So we are gonna use a trick here.
# Use helper function to exploit hypothesis' search strategies.
# Use global variable to track intermediate information.

collision_count = 0
acceptable_collision_rate_threshold = 0.03
total_test_case = 500
min_distinct_test_case = 300
seen_test_cases = set()


@settings(max_examples=total_test_case)
@given(frozensets(hashable_types), frozensets(hashable_types))
def test_hash_different_frozenset_low_collision_rate_helper(
    s1: FrozenSet[Hashable], s2: FrozenSet[Hashable]
) -> None:
    assume(s1 != s2)
    assume({s1, s2} not in seen_test_cases)
    seen_test_cases.add(frozenset({s1, s2}))

    global collision_count
    if hash_frozenset(s1) == hash_frozenset(s2):
        collision_count += 1


@given(just(None))
def test_hash_different_list_low_collision_rate(_: None) -> None:
    assert len(seen_test_cases) > min_distinct_test_case
    assert (
        collision_count / len(seen_test_cases)
    ) < acceptable_collision_rate_threshold
