import json


def extract(body):
    try:
        d = json.loads(body) if isinstance(body, str) else body
    except Exception:
        d = {}
    if isinstance(d, dict) and "detail" in d:
        return json.loads(d["detail"]) if isinstance(d["detail"], str) else d["detail"]
    return d if isinstance(d, dict) else {}
