import argparse
import functools
from collections import defaultdict
from itertools import combinations

from .sbbackupfile import SBBackupFile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", metavar="FILES", nargs="+", help="input files")
    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, help="Enable debug mode"
    )
    args = parser.parse_args()

    for filepath in args.files:
        f = SBBackupFile(filepath)
        # print(f.soup.sessions_hash_set)
        print(list(map(lambda x: len(str(x)), f.soup.sessions_hash_set)))

    # redundancy table
    table = defaultdict(list)

    # since SBBackupFile initialization involves loading a large file into memory and
    # expensive json parsing, for space efficiency, we would like to cache its
    # instance to improve performance.
    SBBackupFile_cached = functools.lru_cache(maxsize=8)(SBBackupFile)
    # cache maxsize can be easily tuned with the observation that

    for filename1, filename2 in combinations(args.files, 2):
        f1 = SBBackupFile_cached(filename1)
        f2 = SBBackupFile_cached(filename2)
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
        print(SBBackupFile_cached.cache_info())


if __name__ == "__main__":
    main()
