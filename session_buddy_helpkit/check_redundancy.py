import json
import os
from collections import namedtuple
from functools import reduce
from itertools import filterfalse
from typing import *

from .utils.hash_utils import hashablize_dict


Digest = namedtuple("Digest", ["filename", "fingerprint"])


def load_json_from_file(filepath: str) -> Dict:
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def extract_digests(filepaths: List[str]) -> List[Digest]:
    digests = []
    for filepath in filepaths:
        json_obj = load_json_from_file(filepath)
        sessions = json_obj["sessions"]
        fingerprint = frozenset(hash(hashablize_dict(session)) for session in sessions)
        digests.append(
            Digest(filename=os.path.basename(filepath), fingerprint=fingerprint)
        )
    return digests


def calculate_sinks(digests: List[Digest]) -> List[Digest]:
    sinks = []
    for digest in digests:
        new = []
        for sink in sinks:
            if not sink.fingerprint.issubset(digest.fingerprint):
                new.append(sink)
        new.append(digest)
        sinks = new
    return sinks


def check_redundancy_imperative_style(filepaths: List[str]) -> None:
    digests = extract_digests(filepaths)
    digests.sort(key=lambda digest: len(digest.fingerprint))
    sinks = calculate_sinks(digests)

    print(f"Scanned {len(filepaths)} files")
    print(f"{len(sinks)} of them are sinks")
    # for sink in sinks:
    #     print(sink.filename)


# TODO: what's the best practice on exception handling in functional programming
def check_redundancy_functional_style(filepaths: List[str]) -> None:
    Digest = namedtuple("Digest", ["filename", "fingerprint"])

    def load_json_from_file(filepath: str) -> Dict:
        # TODO: add handling of exception
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return json.load(f)

    def extract_fingerprint(filepath: str) -> FrozenSet[int]:
        json_obj = load_json_from_file(filepath)
        sessions = json_obj["sessions"]
        return frozenset(hash(hashablize_dict(s)) for s in sessions)

    def calculate_sinks(sinks: List[Digest], digest: Digest) -> List[Digest]:
        return list(
            filterfalse(
                lambda sink: sink.fingerprint.issubset(digest.fingerprint), sinks
            )
        ) + [digest]

    digests = (
        Digest(
            filename=os.path.basename(filepath),
            fingerprint=extract_fingerprint(filepath),
        )
        for filepath in filepaths
    )

    sorted_digests = sorted(digests, key=lambda digest: len(digest.fingerprint))
    sinks = reduce(calculate_sinks, sorted_digests, [])

    print(f"Scanned {len(filepaths)} files")
    print(f"{len(sinks)} of them are sinks")
    # for sink in sinks:
    #     print(sink.filename)
