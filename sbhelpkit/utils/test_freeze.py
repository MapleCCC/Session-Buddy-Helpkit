from typing import *

from hypothesis import given, assume
from hypothesis.strategies import *

from .freeze import *

hashable_types = none() | booleans() | floats() | text()


@given(lists(hashable_types))
def test_freeze_list(l: List[Hashable]) -> None:
    assert freeze_list(l) == freeze_list(l)
    assert hash(freeze_list(l)) == hash(freeze_list(l))


@given(lists(hashable_types), lists(hashable_types))
def test_freeze_list_inequality(l1: List[Hashable], l2: List[Hashable]) -> None:
    assume(l1 != l2)
    assert freeze_list(l1) != freeze_list(l2)
    assert hash(freeze_list(l1)) != hash(freeze_list(l2))


@given(dictionaries(hashable_types, hashable_types))
def test_freeze_dict(d: Dict[Hashable, Hashable]) -> None:
    assert freeze_dict(d) == freeze_dict(d)
    assert hash(freeze_dict(d)) == hash(freeze_dict(d))


@given(
    dictionaries(hashable_types, hashable_types),
    dictionaries(hashable_types, hashable_types),
)
def test_freeze_dict_inequality(ds1: Dict[Hashable], ds2: Dict[Hashable]) -> None:
    assume(ds1 != ds2)
    assert freeze_dict(ds1) != freeze_dict(ds2)
    assert hash(freeze_dict(ds1)) != hash(freeze_dict(ds2))
