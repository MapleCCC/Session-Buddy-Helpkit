import argparse
import json
from collections import defaultdict
from functools import lru_cache
from itertools import combinations
from json import JSONDecodeError

from models import *


def get_soup_from_filename(filename: str) -> SBSoup:
    try:
        # use utf-8-sig instead of utf-8 based on the observation
        # that session buddy backup/export file usually have default
        # `UTF-8 with BOM` encoding. I don't know whether this is due to
        # extension intention or due to my develop environment.
        # But using utf-8-sig is always safer choice and yield better robustness.
        with open(filename, encoding="utf-8-sig") as f:
            return SBSoup(json.load(f))
    except JSONDecodeError:
        raise RuntimeError(f"Error decoding JSON file: {filename}")
    except:
        raise RuntimeError(f"Error parsing JSON file: {filename}")


@lru_cache(4)
class SBBackupFile:
    def __init__(self, filename: str):
        self.filename = filename
        self.soup = get_soup_from_filename(filename)

    def is_redundant_wrt(self, other):
        assert isinstance(other, self.__class__)
        return self.soup.sessions_hash_set.issubset(other.soup.sessions_hash_set)

    def similarity(self, other):
        assert isinstance(other, self.__class__)
        return set_similarity(self.soup.sessions_hash_set, other.soup.sessions_hash_set)


def compare_set(s1: set, s2: set):
    if s1.isdisjoint(s2):
        print("Disjoin")
    if s1 <= s2:
        print("Subset")
    if s1 >= s2:
        print("Superset")
    print(f"Set one has {len(s1)} elements, set two has {len(s2)} elements.")
    print(f"They have {len(s1.difference(s2))} elements different")
    print(f"They have {len(s1.intersection(s2))} elements in common")


def set_similarity(s1: set, s2: set):
    return len(s1.intersection(s2)) / len(s1.union(s2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", metavar="FILES", nargs="+", help="input files")
    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, help="Enable debug mode"
    )
    args = parser.parse_args()

    # redundancy table
    table = defaultdict(list)

    for filename1, filename2 in combinations(args.files, 2):
        f1 = SBBackupFile(filename1)
        f2 = SBBackupFile(filename2)
        if f1.is_redundant_wrt(f2):
            table[f1].append(f2)
        elif f2.is_redundant_wrt(f1):
            table[f2].append(f1)
        else:
            similarity = f1.similarity(f2)
            if similarity > 0:
                print(
                    f"Similarity between {f1.filename} and {f2.filename} is {similarity:.2f}"
                )

    print(f"Found {len(table)} redundancy relation{'s' if len(table) > 1 else ''}")

    if args.debug:
        print(SBBackupFile.cache_info())


if __name__ == "__main__":
    main()
