from hypothesis.strategies import *
from string import printable

__all__ = ["jsons", "json_noncontainers"]


# Hypothesis strategy for generating JSON data.
# Reference: https://hypothesis.readthedocs.io/en/latest/data.html#recursive-data
jsons = recursive(
    none() | booleans() | floats() | text(printable),
    lambda children: lists(children, 1)
    | dictionaries(text(printable), children, min_size=1),
)

json_noncontainers = none() | booleans() | floats() | text(printable)
