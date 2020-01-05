from typing import *

__all__ = ["compare_set", "set_similarity"]


SetType = Union[Set, FrozenSet]


def compare_set(s1: SetType, s2: SetType) -> None:
    if s1.isdisjoint(s2):
        print("Disjoin")
    if s1 <= s2:
        print("Subset")
    if s1 >= s2:
        print("Superset")
    print(
        f"Set one has {len(s1)} elements, set two has {len(s2)} elements.\n"
        f"They have {len(s1.difference(s2))} elements in different.\n"
        f"They have {len(s1.intersection(s2))} elements in common.\n"
    )


def set_similarity(s1: SetType, s2: SetType) -> float:
    return len(s1.intersection(s2)) / len(s1.union(s2))
