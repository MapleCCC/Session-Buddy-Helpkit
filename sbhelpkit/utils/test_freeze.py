from typing import *

from hypothesis import given
from hypothesis.strategies import *

from freeze import *


@given(lists(integers()))
def test_freeze_list(l: List[int]) -> None:
    assert freeze_list(l) == freeze_list(l)
    assert hash(freeze_list(l)) == hash(freeze_list(l))


@given(dictionaries(integers(), integers()))
def test_freeze_dict(d: Dict[int, int]) -> None:
    assert freeze_dict(d) == freeze_dict(d)
    assert hash(freeze_dict(d)) == hash(freeze_dict(d))
