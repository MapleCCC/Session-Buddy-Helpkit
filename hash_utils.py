from typing import Hashable, List

sentinel = object()


def hasattrs(obj, names: List[str])->bool:
    for name in names:
        if not hasattr(obj, name):
            return False
    return True


def hashablize_list(l: list)->tuple:
    """
    This function provides a one-to-one mapping from a list instance
    to a tuple. The mapped tuple is guaranteed to contain only hashable
    elements, hence the tuple itself becomes hashable.

    Highly likely no two different lists are mapped to a same tuple.
    Two eqaul lists yield the same tuple.

    If the mapping cannot be found for some lists, a ValueError will be raised.
    """
    tmp = []
    for item in l:
        if isinstance(item, Hashable):
            tmp.append(item)
        elif isinstance(item, list):
            tmp.append(hashablize_list(item))
        elif isinstance(item, dict):
            tmp.append(hashablize_dict(item))
        else:
            raise ValueError(
                f"Cannot hashablize unsupported type {type(item)}")
    return tuple(tmp)


def hashablize_dict(d: dict)->tuple:
    """
    This function provides a one-to-one mapping from a dict instance
    to a tuple. The mapped tuple is guaranteed to contain only hashable
    elements, hence the tuple itself becomes hashable.

    Highly likely no two different dicts are mapped to a same tuple.
    Two eqaul dicts yield the same tuple.

    If the mapping cannot be found for some dicts, a ValueError will be raised.
    """
    tmp = []
    for k, v in d.items():
        if isinstance(v, Hashable):
            tmp += [k, v, sentinel]
        elif isinstance(v, list):
            tmp += [k, hashablize_list(v), sentinel]
        elif isinstance(v, dict):
            tmp += [k, hashablize_dict(v), sentinel]
        else:
            raise ValueError(f"Cannot hashablize unsupported type {type(v)}")
    return tuple(tmp)


# def hashable(obj):
#     # Note that it's actually a sanity check. We need one more criteria
#     # to confirm hashability, that is, two equal objects should yield
#     # the same hash value.
#     return hasattrs(obj, ['__hash__', '__eq__'])


# def hashable_sanity_check(obj)->bool:
#     """
#     Compared to test by try hash(obj) and see if there will be exception,
#     this method is not guarantee that the (hence the name sanity check) but faster.
#     """
#     if isinstance(obj, [int, str, bool, type(None)]):
#         return True
#     return hasattrs(obj, ['__hash__', '__eq__'])


# def hashable(obj):
#     try:
#         hash(obj)
#     except:
#         return False
#     else:
#         return True
