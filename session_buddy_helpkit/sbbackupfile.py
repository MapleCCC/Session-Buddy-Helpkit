import json
from json import JSONDecodeError

from .models import SBSoup
from .utils.set_utils import compare_set, set_similarity


def get_soup_from_filename(filename: str) -> SBSoup:
    try:
        # use utf-8-sig instead of utf-8 based on the observation
        # that session buddy backup/export file usually have default
        # `UTF-8 with BOM` encoding. I don't know whether this is due to
        # extension intention or due to my develop environment.
        # But using utf-8-sig is always safer choice and yield better robustness.
        with open(filename, "r", encoding="utf-8-sig") as f:
            return SBSoup(json.load(f))
    except JSONDecodeError:
        raise RuntimeError(f"Error decoding JSON file: {filename}")
    except:
        raise RuntimeError(f"Error parsing JSON file: {filename}")


# @functools.lru_cache(maxsize=8)
class SBBackupFile:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.soup = get_soup_from_filename(filename)

    # TODO: type annotation for the "other" argument is not available for now.
    # Until self type reference is supported by Python officially.
    def is_redundant_wrt(self, other) -> bool:
        # use self.__class__ instead of SBBackupFile so that
        # the type check works correctly even when our class is wrapped
        # by functools.lru_cache
        assert isinstance(other, self.__class__)
        return self.soup.sessions_hash_set.issubset(other.soup.sessions_hash_set)

    # TODO: type annotation for the "other" argument is not available for now.
    # Until self type reference is supported by Python officially.
    def similarity(self, other) -> float:
        # use self.__class__ instead of SBBackupFile so that
        # the type check works correctly even when our class is wrapped
        # by functools.lru_cache
        assert isinstance(other, self.__class__)
        return set_similarity(self.soup.sessions_hash_set, other.soup.sessions_hash_set)
