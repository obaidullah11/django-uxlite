import re

from . import settings_defaults as cfg

_TOKEN_SPLIT_RE = re.compile(r"[^a-zA-Z0-9]+|(?<=[a-z0-9])(?=[A-Z])")


def _tokens(key):
    return {
        token.lower()
        for token in _TOKEN_SPLIT_RE.split(str(key))
        if token
    }


def _is_sensitive(key):
    key_tokens = _tokens(key)
    for field in cfg.SENSITIVE_FIELDS:
        field_tokens = _tokens(field)
        if field_tokens and field_tokens <= key_tokens:
            return True
    return False


def mask_payload(data):
    """Recursively mask sensitive keys in dicts/lists. Returns a new structure;
    never mutates the input, since callers may still need the original object."""
    if isinstance(data, dict):
        return {
            key: (cfg.MASK_VALUE if _is_sensitive(key) else mask_payload(value))
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [mask_payload(item) for item in data]
    return data
