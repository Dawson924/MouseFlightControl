from typing import List

from type.script import ScriptOption


def get_default(options: List[ScriptOption]):
    default = {}
    for a, b, c in options:
        default[a] = c
    return default


def get_defaults(options: List[List[ScriptOption]]):
    arr = []
    for a in options:
        arr.append(get_default(a))
    return arr
