from typing import Hashable, List, Tuple, Dict

__all__ = ["freeze_dict", "freeze_list"]

list_begin_sentinel = object()
list_end_sentinel = object()
dict_begin_sentinel = object()
dict_end_sentinel = object()


# TODO: Do we want to have no two different lists mapping to a same tuple,
# or do we want to have no two different objects mapping to a same tuple.
def freeze_list(l: List) -> Tuple:
    """
    This function provides a one-to-one mapping from a list instance
    to a tuple instance. The mapped tuple is guaranteed to contain only hashable
    elements, hence the tuple itself becomes hashable.

    Highly likely no two different lists are mapped to a same tuple.
    Two eqaul lists yield the same tuple.

    If the mapping cannot be found for some lists, a ValueError will be raised.
    """
    tmp = []
    tmp.append(list_begin_sentinel)
    for item in l:
        if isinstance(item, Hashable):
            tmp.append(item)
        elif isinstance(item, list):
            tmp.append(freeze_list(item))
        elif isinstance(item, dict):
            tmp.append(freeze_dict(item))
        else:
            raise ValueError(f"Cannot freeze unsupported type {type(item)}")
    tmp.append(list_end_sentinel)
    return tuple(tmp)


def freeze_dict(d: Dict) -> FrozenSet:
    """
    This function provides a one-to-one mapping from a dict instance
    to a tuple instance. The mapped tuple is guaranteed to contain only hashable
    elements, hence the tuple itself becomes hashable.

    Highly likely no two different dicts are mapped to a same tuple.
    Two eqaul dicts yield the same tuple.

    If the mapping cannot be found for some dicts, a ValueError will be raised.
    """

    def mapper(item):
        if isinstance(item, Hashable):
            return item
        elif isinstance(item, list):
            return freeze_list(item)
        elif isinstance(item, dict):
            return freeze_dict(item)
        else:
            raise ValueError(f"Cannot freeze unsupported type {type(item)}")

    return frozenset(
        itertools.chain(
            [dict_begin_sentinel], map(mapper, d.items()), [dict_end_sentinel]
        )
    )


def freeze_dict_using_tuple_method(d: Dict) -> Tuple:
    tmp = []
    tmp.append(dict_begin_sentinel)
    for k, v in sorted(d.items()):
        if isinstance(v, Hashable):
            tmp += [k, v]
        elif isinstance(v, list):
            tmp += [k, freeze_list(v)]
        elif isinstance(v, dict):
            tmp += [k, freeze_dict(v)]
        else:
            raise ValueError(f"Cannot freeze unsupported type {type(v)}")
    tmp.append(dict_end_sentinel)
    return tuple(tmp)
