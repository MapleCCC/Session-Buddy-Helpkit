# from ..pyobjhash.hash_frozenset import *
from .hash_frozenset import *
from hypothesis import given
from hypothesis.strategies import *
from string import printable


# Hypothesis strategy for generating JSON data.
# Reference: https://hypothesis.readthedocs.io/en/latest/data.html#recursive-data
jsons = recursive(
    none() | booleans() | floats() | text(printable),
    lambda children: lists(children, 1)
    | dictionaries(text(printable), children, min_size=1),
)

json_noncontainers = none() | booleans() | floats() | text(printable)


@given(frozensets(integers()))
def test_hash_frozenset(s: FrozenSet[int]) -> None:
    assert hash_frozenset(s) == hash(s)


@given(frozensets(json_noncontainers))
def test_hash_frozenset_of_jsonobjects(s):
    assert hash_frozenset(s) == hash(s)
