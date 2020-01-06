from typing import *

from hypothesis import given, assume
from hypothesis.strategies import *

from freeze import *


@given(lists(integers()))
def test_freeze_list(l: List[int]) -> None:
    assert freeze_list(l) == freeze_list(l)
    assert hash(freeze_list(l)) == hash(freeze_list(l))


# TODO: test over list of heterogeneous type of elements
# @given(lists())
# def test_freeze_list_soundness(l: List) -> None:
#     assert freeze_list(l) == freeze_list(l)
#     assert hash(freeze_list(l)) == hash(freeze_list(l))


@given(lists(integers()), lists(integers()))
def test_freeze_list_inequality(l1: List[int], l2: List[int]) -> None:
    assume(l1 != l2)
    assert freeze_list(l1) != freeze_list(l2)
    assert hash(freeze_list(l1)) != hash(freeze_list(l2))


@given(dictionaries(integers(), integers()))
def test_freeze_dict(d: Dict[int, int]) -> None:
    assert freeze_dict(d) == freeze_dict(d)
    assert hash(freeze_dict(d)) == hash(freeze_dict(d))


# TODO: test over dictionary of heterogeneous type of items
# @given(dictionaries())
# def test_freeze_dict_soundness(d: Dict) -> None:
#     assert freeze_dict(d) == freeze_dict(d)
#     assert hash(freeze_dict(d)) == hash(freeze_dict(d))


@given(dictionaries(integers(), integers()), dictionaries(integers(), integers()))
def test_freeze_dict_inequality(ds1: Dict[int, int], ds2: Dict[int, int]) -> None:
    assume(ds1 != ds2)
    assert freeze_dict(ds1) != freeze_dict(ds2)
    assert hash(freeze_dict(ds1)) != hash(freeze_dict(ds2))
