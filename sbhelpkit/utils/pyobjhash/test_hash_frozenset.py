from typing import *

from hypothesis import given
from hypothesis.strategies import *

from .hash_frozenset import *

hashable_types = none() | booleans() | floats() | text()


@given(frozensets(hashable_types))
def test_hash_frozenset(s: FrozenSet) -> None:
    assert hash_frozenset(s) == hash(s)


@given(frozensets(hashable_types))
def test_frozensethasher(s: FrozenSet) -> None:
    sh = FrozenSetHasher()
    for item in s:
        sh.update(item)
    assert sh.digest() == hash(s)


# TODO: test on nested frozenset
