from typing import *

# Reference:
# https://docs.python.org/3/library/json.html#encoders-and-decoders
# https://github.com/python/typing/issues/182#issuecomment-186684288
JSONType = Union[
    Dict[str, Any], List[Any], str, int, float, bool, None,
]
JSONObject = Dict[str, Any]
JSONArray = List[Any]
