from hash_utils import *
from hypothesis import given
from hypothesis.strategies import *
from typing import *


@given(lists(integers()))
def test_hashablize_list(l: List[int]) -> None:
    assert hashablize_list(l) == hashablize_list(l)
    assert hash(hashablize_list(l)) == hash(hashablize_list(l))


@given(dictionaries(integers(), integers()))
def test_hashablize_dict(d: Dict[int, int]) -> None:
    assert hashablize_dict(d) == hashablize_dict(d)
    assert hash(hashablize_dict(d)) == hash(hashablize_dict(d))
