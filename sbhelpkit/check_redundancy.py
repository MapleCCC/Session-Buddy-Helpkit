import itertools
import json
import os
import time
from collections import namedtuple
from functools import reduce
from json import JSONDecodeError
from typing import *

from .utils.extra_typings import *
from .utils.freeze import freeze_dict

try:
    profile
except NameError:
    profile = lambda f: f


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


@profile  # type: ignore  # https://github.com/rkern/line_profiler
def check_redundancy_by_guid(filepaths: List[str]) -> None:
    Fingerprint = FrozenSet[str]
    Meta = NamedTuple("Meta", [("filename", str), ("fingerprint", Fingerprint)])

    def extract_fingerprint(jsonobj: JSONObject) -> Fingerprint:
        sesses = jsonobj["sessions"]
        return frozenset((sess["gid"] for sess in sesses if sess["type"] != "current"))

    def reducer(sinks: Iterable[Meta], meta: Meta) -> Iterable[Meta]:
        return itertools.chain(
            (meta,),
            filter(lambda x: not x.fingerprint.issubset(meta.fingerprint), sinks),
        )

    jsonobjs = map(load_json_from_file, filepaths)
    fingerprints = map(extract_fingerprint, jsonobjs)
    filenames = map(os.path.basename, filepaths)
    metas = itertools.starmap(Meta, zip(filenames, fingerprints))
    metas = sorted(metas, key=lambda x: len(x.fingerprint))
    sinks: Iterable[Meta] = reduce(reducer, sorted_metas, [])

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
@profile  # type: ignore
def check_redundancy_functional_style(filepaths: List[str]) -> None:
    Meta = NamedTuple("Digest", [("filename", str), ("fingerprint", frozenset)])

    def load_json_from_file(filepath: str) -> Dict:
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                rbuf = f.read()
                if rbuf.startswith("\uFEFF"):
                    rbuf = rbuf.encode("utf-8")[3:].decode("utf-8")
                return json.loads(rbuf)
        except:
            raise RuntimeError(f"Error parsing json file: {filepath}")

    def extract_fingerprint(filepath: str) -> FrozenSet[int]:
        json_obj = load_json_from_file(filepath)
        sessions = json_obj["sessions"]
        return frozenset(
            hash(freeze_dict(s)) for s in sessions if s["type"] != "current"
        )

    def calculate_sinks(sinks: Iterable[Meta], meta: Meta) -> Iterable[Meta]:
        return itertools.chain(
            itertools.filterfalse(
                lambda sink: sink.fingerprint.issubset(meta.fingerprint), sinks
            ),
            [meta],
        )

    metas = (
        Meta(
            filename=os.path.basename(filepath),
            fingerprint=extract_fingerprint(filepath),
        )
        for filepath in filepaths
    )

    sorted_metas = sorted(metas, key=lambda meta: len(meta.fingerprint))
    sinks = reduce(calculate_sinks, sorted_metas, [])

    print(f"Scanned {len(filepaths)} files")
    print(f"{len(list(sinks))} of them are sinks")
    for sink in sinks:
        print(sink.filename)


check_redundancy = check_redundancy_by_guid
