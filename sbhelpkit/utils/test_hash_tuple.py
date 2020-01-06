from typing import *

from hypothesis import given
from hypothesis.strategies import *

from tuplehash import *


@given(lists(integers()))
def test_hash_tuple_compliance(l: List[int]) -> None:
    t = tuple(l)
    assert hash_tuple(t) == hash(t)
