import argparse
import json
from collections import defaultdict
from itertools import combinations

from models import *


def get_soup_from_filename(filename: str)-> SBSoup:
    with open(filename, encoding='utf-8-sig') as f:
        return SBSoup(json.load(f))


class SBBackupFile:
    def __init__(self, filename: str):
        self.filename = filename
        self.soup = get_soup_from_filename(filename)

    def is_redundant_wrt(self, other):
        assert isinstance(other, SBBackupFile)
        return self.soup.sessions_hash_set.issubset(
            other.soup.sessions_hash_set)

    def similarity(self, other):
        assert isinstance(other, SBBackupFile)
        return set_similarity(
            self.soup.sessions_hash_set,
            other.soup.sessions_hash_set)


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
    parser.add_argument(
        'files',
        metavar='FILES',
        nargs='+',
        help="input files")
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
                    f'Similarity between {f1.filename} and {f2.filename} is {similarity:.2f}')

    print(f"Found {len(table)} redundancy relation{'s' if len(table) > 1 else ''}")


if __name__ == '__main__':
    main()
