# django-uxlite

Reusable Django app that adds UXCam-style **request/event analytics**, **crash logging**,
and **PII masking** to API services (Django REST Framework friendly), all viewable in
Django admin. No client-side JS or session replay — built for API-only backends.

## Install

```bash
pip install -e /path/to/django-uxlite
```

## Setup

1. Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "uxlite",
]
```

2. Add the middleware (near the top, after auth middleware so `request.user` is set):

```python
MIDDLEWARE = [
    ...,
    "uxlite.middleware.UXLiteTrackingMiddleware",
]
```

3. Migrate:

```bash
python manage.py migrate uxlite
```

4. Optional settings (all have defaults, see `uxlite/settings_defaults.py`):

```python
UXLITE_SENSITIVE_FIELDS = ["password", "token", "email", "card_number", "ssn"]
UXLITE_RETENTION_DAYS = 90
UXLITE_MASK_VALUE = "***"
UXLITE_TRACK_PATHS_EXCLUDE = ["/admin/", "/static/", "/health/"]
```

## Usage

### Custom events

```python
from uxlite.tracking import track_event

def checkout_view(request):
    ...
    track_event("checkout_completed", request=request, meta={"order_id": order.id, "email": user.email})
```

Sensitive keys in `meta` are masked automatically before being stored, based on
`UXLITE_SENSITIVE_FIELDS`.

### Crash logging

Wired up automatically via the `got_request_exception` signal — no extra code needed.
Every unhandled exception in a request is logged to `CrashLog`.

### Purge old data

```bash
python manage.py uxlite_purge
```

Deletes `RequestLog`, `Event`, and `CrashLog` rows older than `UXLITE_RETENTION_DAYS`.
`Session` rows with no remaining `RequestLog`/`Event` rows are cleaned up too.

### Admin

Everything (`RequestLog`, `Session`, `Event`, `CrashLog`) is registered in Django admin
with search/filter support — no extra dashboard UI needed.

## Out of scope (v1)

- Pixel-accurate session replay (DOM/gesture recording)
- AI-analyst / auto-insight generation
- Client-side JS heatmaps
