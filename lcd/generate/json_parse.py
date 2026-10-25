"""Extract a JSON object from a model reply."""

from __future__ import annotations

import json


def json_obj(raw: str):
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no json")
    return json.loads(raw[start : end + 1])
