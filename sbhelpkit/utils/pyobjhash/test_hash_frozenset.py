from typing import *

from hypothesis import given
from hypothesis.strategies import *

from .hash_frozenset import *

hashable_types = none() | booleans() | floats() | text()


@given(frozensets(hashable_types))
def test_hash_frozenset(s: FrozenSet) -> None:
    assert hash_frozenset(s) == hash(s)


@given(frozensets(hashable_types))
def test_hash_frozenset_of_jsonobjects(s):
    assert hash_frozenset(s) == hash(s)
