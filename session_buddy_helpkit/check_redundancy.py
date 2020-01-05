import json
import os
from collections import namedtuple
from functools import reduce
from itertools import filterfalse
from json import JSONDecodeError
from typing import *

from .utils.hash_utils import hashablize_dict


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


def extract_digests(filepaths: List[str], report: Dict[str, List[str]]) -> List[Digest]:
    digests = []
    for filepath in filepaths:
        report["scanned"].append(filepath)
        try:
            json_obj = load_json_from_file(filepath)
        except Exception:
            report["unparsed"].append(filepath)
            continue
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
    report = {"scanned": [], "unparsed": [], "sinks": []}

    digests = extract_digests(filepaths, report)
    digests.sort(key=lambda digest: len(digest.fingerprint))
    sinks = calculate_sinks(digests)

    print(f"Scanned {len(filepaths)} files")
    print(f"{len(report['unparsed'])} unparsed")
    print(f"{len(sinks)} of them are sinks")
    # print(report)
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


check_redundancy = check_redundancy_imperative_style
