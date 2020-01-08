import json
import os
import time
from collections import namedtuple
from functools import reduce
from itertools import filterfalse, zip_longest, chain
from json import JSONDecodeError
from typing import *

from .utils.extra_typings import *
from .utils.freeze import freeze_dict


Digest = namedtuple("Digest", ["filename", "fingerprint"])


def load_json_from_file(filepath: str) -> Dict:
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            rbuf = f.read()
            # strip the BOM head if the format is "UTF-8 with BOM"
            if rbuf.startswith("\ufeff"):
                rbuf = rbuf.encode("utf-8")[3:].decode("utf-8")
            return json.loads(rbuf)
    except JSONDecodeError:
        raise RuntimeError(f"Error decoding JSON file: {filepath}")
    except:
        raise RuntimeError(f"Error parsing JSON file: {filepath}")


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


def check_redundancy_by_guid(filepaths: List[str]) -> None:
    def extract_fingerprint(jsonobj: JSONObject) -> FrozenSet[str]:
        sesses = jsonobj["sessions"]
        assert sesses[0]["type"] == "current"
        # return frozenset((sess["gid"] for sess in sesses if sess["type"] != "current"))
        return frozenset((sess["gid"] for sess in sesses[1:]))

    def reducer(
        sinks: Iterable[Tuple[str, FrozenSet]], meta: Tuple[str, FrozenSet]
    ) -> Iterable[Tuple[str, FrozenSet]]:
        return chain([meta], filter(lambda x: not x[1].issubset(meta), sinks))

    jsonobjs = (load_json_from_file(filepath) for filepath in filepaths)
    fingerprints = (extract_fingerprint(jsonobj) for jsonobj in jsonobjs)
    metas = zip_longest(filepaths, fingerprints)
    metas = sorted(metas, key=lambda x: x[1])
    sinks = reduce(reducer, metas, [])

    print(f"{len(filepaths)} files scanned")
    print(f"{len(list(sinks))} sinks found")


def check_redundancy_imperative_style(filepaths: List[str]) -> None:
    print("Begin to extract digests...")
    digests_extraction_begin_time = time.time()
    digests = extract_digests(filepaths)
    digests_extraction_end_time = time.time()
    print("Complete extraction of digests")

    digests.sort(key=lambda digest: len(digest.fingerprint))

    print("Begin to calculate sinks")
    sinks_calculation_begin_time = time.time()
    sinks = calculate_sinks(digests)
    sinks_calculation_end_time = time.time()
    print("Complete calculating sinks")

    print(f"Scanned {len(filepaths)} files")
    print(f"{len(sinks)} of them are sinks")
    print(
        f"{(digests_extraction_end_time - digests_extraction_begin_time):.2f} seconds spent on digests extreaction"
    )
    print(
        f"{(sinks_calculation_end_time - sinks_calculation_begin_time):.2f} seconds spent on sinks calculation"
    )
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
        return frozenset(hash(freeze_dict(s)) for s in sessions)

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


check_redundancy = check_redundancy_by_guid
