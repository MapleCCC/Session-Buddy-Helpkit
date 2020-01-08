from typing import *

# Reference: https://docs.python.org/3/library/json.html#encoders-and-decoders
JSONType = Union[
    Dict["JSONType", "JSONType"],
    List["JSONType"],
    Tuple["JSONType", ...],
    str,
    int,
    float,
    bool,
    None,
]

JSONObject = Dict[JSONType, JSONType]
JSONArray = List[JSONType]

jsontype_container_type_hint = (
    Dict["JSONType", "JSONType"],
    List["JSONType"],
    Tuple["JSONType", ...],
)
jsontype_container_type = frozenset((dict, list, tuple))

jsontype_noncontainer_type_hint = (str, int, float, bool, None)
jsontype_noncontainer_type = frozenset((str, int, float, bool, type(None)))
