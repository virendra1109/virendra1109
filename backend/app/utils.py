import base64
import json
from typing import Any


def to_base64_data_uri(data: bytes, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(data).decode("utf-8")


def decode_json_first(text: str) -> Any:
    try:
        decoder = json.JSONDecoder()
        pos = 0
        json_objects = []
        while pos < len(text):
            try:
                obj, pos = decoder.raw_decode(text, pos)
                json_objects.append(obj)
            except json.JSONDecodeError:
                pos += 1
            except Exception:
                pos += 1
        return json_objects[0] if json_objects else {}
    except Exception:
        return {"system": "Critical error received"}
