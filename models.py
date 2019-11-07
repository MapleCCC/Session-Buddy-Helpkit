from hash_utils import hashablize_dict


class DictProxy(object):
    """A sementic and readonly dict-type object wrapper"""

    def __init__(self, dic: dict):
        self._dic = dic

    __slots__ = '_dic'

    def __getitem__(self, key):
        return self._dic[key]

    def __hash__(self):
        return hash(hashablize_dict(self._dic))

    def __eq__(self, other):
        assert isinstance(other, self.__class__)
        return hash(self) == hash(other)


class SBSoup(DictProxy):
    def __init__(self, dic: dict):
        super().__init__(dic)
        self._sessions_hash_set = None

    __slots__ = '_sessions_hash_set'

    @property
    def sessions_hash_set(self):
        # lazy calculation, cache result, to save performance overhead
        # as the calculation here is expensive
        # TODO: need profiling to confirm
        if self._sessions_hash_set is None:
            self._sessions_hash_set = frozenset(map(hash, self.sessions))
        return self._sessions_hash_set

    @property
    def sessions(self):
        return list(map(Session, self._dic['sessions']))


class Session(DictProxy):
    @property
    def windows(self):
        return list(map(Window, self._dic['windows']))


class Window(DictProxy):
    @property
    def tabs(self):
        return list(map(Tab, self._dic['tabs']))


class Tab(DictProxy):
    pass
