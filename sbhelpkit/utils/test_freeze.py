import sys
from typing import *

from hypothesis import given, assume, settings
from hypothesis.strategies import *

from .freeze import freeze_list, freeze_dict, hash_list, hash_dict


if sys.version_info < (3, 7):
    raise RuntimeError("Do not run test under v3.7.0. "
        "We need built-in hash implementation up to v3.7.0 to test against.")

hashable_types = none() | booleans() | floats() | text()

# TODO: decide a collision rate as threshold for being acceptable.
acceptable_collision_rate_threshold = 0.03

# TODO: test over nestd lists and nested dicts
# TODO: test raise exception when encountering unhashable input

@given(lists(hashable_types))
def test_freeze_list_regression(l: List[Hashable]) -> None:
    assert freeze_list(l) == freeze_list(l)
    assert hash(freeze_list(l)) == hash(freeze_list(l))


freeze_list_test_collision_count = 0
freeze_list_total_test_case = 500
freeze_list_min_distinct_test_case = 300
freeze_list_seen_test_cases= set()


@settings(max_examples=freeze_list_total_test_case)
@given(lists(hashable_types), lists(hashable_types))
def test_freeze_list_inequality(l1: List[Hashable], l2: List[Hashable]) -> None:
    assume(l1 != l2)
    t1, t2 = tuple(l1), tuple(l2)
    assume({t1, t2} not in freeze_list_seen_test_cases)
    freeze_list_seen_test_cases.add(frozenset({t1, t2}))

    assert freeze_list(l1) != freeze_list(l2)

    global freeze_list_test_collision_count
    if hash(freeze_list(l1)) == hash(freeze_list(l2)):
        freeze_list_test_collision_count += 1


@settings(max_examples=freeze_list_total_test_case)
@given(just(None))
def test_freeze_list_low_collision_rate(_: None) -> None:
    assert len(freeze_list_seen_test_cases) > freeze_list_min_distinct_test_case
    assert (
        freeze_list_test_collision_count / len(freeze_list_seen_test_cases)
    ) < acceptable_collision_rate_threshold


@given(dictionaries(hashable_types, hashable_types))
def test_freeze_dict_regression(d: Dict[Hashable, Hashable]) -> None:
    assert freeze_dict(d) == freeze_dict(d)
    assert hash(freeze_dict(d)) == hash(freeze_dict(d))


freeze_dict_test_collision_count = 0
freeze_dict_total_test_case = 500
freeze_dict_min_distinct_test_case = 300
freeze_dict_seen_test_cases = set()


@settings(max_examples=freeze_dict_total_test_case)
@given(
    dictionaries(hashable_types, hashable_types),
    dictionaries(hashable_types, hashable_types),
)
def test_freeze_dict_inequality(
    d1: Dict[Hashable, Hashable], d2: Dict[Hashable, Hashable]
) -> None:
    assume(d1 != d2)
    s1, s2 = frozenset(d1), frozenset(d2)
    assume({s1, s2} not in freeze_dict_seen_test_cases)
    freeze_dict_seen_test_cases.add(frozenset({s1, s2}))

    assert freeze_dict(d1) != freeze_dict(d2)

    global freeze_dict_test_collision_count
    if hash(freeze_dict(d1)) == hash(freeze_dict(d2)):
        freeze_dict_test_collision_count += 1


@given(just(None))
def test_freeze_dict_low_collision_rate(_: None) -> None:
    assert len(freeze_dict_seen_test_cases) > freeze_dict_min_distinct_test_case
    assert (
        freeze_dict_test_collision_count / len(freeze_dict_seen_test_cases)
    ) < acceptable_collision_rate_threshold


@given(lists(hashable_types))
def test_hash_list_regression(l: List[Hashable]) -> None:
    assert hash_list(l) == hash(freeze_list(l))


@given(dictionaries(hashable_types, hashable_types))
def test_hash_dict_regression(d: Dict[Hashable, Hashable]) -> None:
    assert hash_dict(d) == hash(freeze_dict(d))
