from typing import *

from hypothesis import given, assume
from hypothesis.strategies import *

from .freeze import *

hashable_types = none() | booleans() | floats() | text()

# TODO: decide a collision rate as threshold for being acceptable.
acceptable_collision_rate_threshold = 0.03


@given(lists(hashable_types))
def test_freeze_list(l: List[Hashable]) -> None:
    assert freeze_list(l) == freeze_list(l)
    assert hash(freeze_list(l)) == hash(freeze_list(l))


freeze_list_test_collision_count = 0
freeze_list_test_total_count = 0


@given(lists(hashable_types), lists(hashable_types))
def test_freeze_list_inequality(l1: List[Hashable], l2: List[Hashable]) -> None:
    global freeze_list_test_collision_count, freeze_list_test_total_count
    assume(l1 != l2)
    assert freeze_list(l1) != freeze_list(l2)
    if hash(freeze_list(l1)) == hash(freeze_list(l2)):
        freeze_list_test_collision_count += 1
    freeze_list_test_total_count += 1


@given(just(None))
def test_freeze_list_low_collision_rate(_: None) -> None:
    global freeze_list_test_collision_count, freeze_list_test_total_count
    assert freeze_list_test_total_count >= 100
    assert (
        freeze_list_test_collision_count / freeze_list_test_total_count
    ) < acceptable_collision_rate_threshold


@given(dictionaries(hashable_types, hashable_types))
def test_freeze_dict(d: Dict[Hashable, Hashable]) -> None:
    assert freeze_dict(d) == freeze_dict(d)
    assert hash(freeze_dict(d)) == hash(freeze_dict(d))


freeze_dict_test_total_count = 0
freeze_dict_test_collision_count = 0


@given(
    dictionaries(hashable_types, hashable_types),
    dictionaries(hashable_types, hashable_types),
)
def test_freeze_dict_inequality(
    d1: Dict[Hashable, Hashable], d2: Dict[Hashable, Hashable]
) -> None:
    global freeze_dict_test_collision_count, freeze_dict_test_total_count
    assume(d1 != d2)
    assert freeze_dict(d1) != freeze_dict(d2)
    if hash(freeze_dict(d1)) == hash(freeze_dict(d2)):
        freeze_dict_test_collision_count += 1
    freeze_dict_test_total_count += 1


@given(just(None))
def test_freeze_dict_low_collision_rate(_: None) -> None:
    global freeze_dict_test_total_count, freeze_dict_test_collision_count
    assert freeze_dict_test_total_count >= 100
    assert (
        freeze_dict_test_collision_count / freeze_dict_test_total_count
    ) < acceptable_collision_rate_threshold


@given(lists(hashable_types))
def test_hash_list(l: List[Hashable]) -> None:
    assert hash_list(l) == hash(freeze_list(l))


@given(dictionaries(hashable_types, hashable_types))
def test_hash_dict(d: Dict[Hashable, Hashable]) -> None:
    assert hash_dict(d) == hash(freeze_dict(d))
