from hash_utils import *


def test_hashablize_list():
    assert hashablize_list([]) == hashablize_list([])
    assert hash(hashablize_list([])) == hash(hashablize_list([]))
    assert hashablize_list([1]) == hashablize_list([1])
    assert hash(hash(hashablize_list([1]))) == hash(hashablize_list([1]))
    assert hashablize_list([1, 2]) == hashablize_list([1, 2])
    assert hash(hashablize_list([1, 2])) == hash(hashablize_list([1, 2]))


def test_hashablize_dict():
    assert hashablize_dict({}) == hashablize_dict({})
    assert hash(hashablize_dict({})) == hash(hashablize_dict({}))
    assert hashablize_dict({1: 10}) == hashablize_dict({1: 10})
    assert hash(hashablize_dict({1: 10})) == hash(hashablize_dict({1: 10}))
    assert hashablize_dict({1: 10, 2: 20}) == hashablize_dict({1: 10, 2: 20})
    assert hash(hashablize_dict({1: 10, 2: 20})) == hash(hashablize_dict({1: 10, 2: 20}))
