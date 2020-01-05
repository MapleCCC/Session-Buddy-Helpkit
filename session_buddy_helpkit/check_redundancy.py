import json
import os
from collections import namedtuple
from functools import reduce
from itertools import filterfalse
from typing import *

from .utils.hash_utils import hashablize_dict


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
