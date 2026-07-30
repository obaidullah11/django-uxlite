from . import settings_defaults as cfg


def _is_sensitive(key):
    key_lower = str(key).lower()
    return any(field.lower() in key_lower for field in cfg.SENSITIVE_FIELDS)


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
