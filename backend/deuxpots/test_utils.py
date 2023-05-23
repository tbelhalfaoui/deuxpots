from hashlib import sha256
import json
from requests.structures import CaseInsensitiveDict


def request_fingerprint(req):
    field_names = ["method", "url", "headers", "body"]
    req_fields = {}
    for field_name in field_names:
        value = getattr(req, field_name)
        if isinstance(value, CaseInsensitiveDict):
            req_fields[field_name] = json.dumps(dict(value), sort_keys=True)
        elif callable(value):
            req_fields[field_name] = value()
        else:
            req_fields[field_name] = value
    return sha256(json.dumps(req_fields, sort_keys=False).encode()).hexdigest()
