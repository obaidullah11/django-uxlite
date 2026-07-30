# What `pip install django-uxlite` gives you

A drop-in Django app that adds analytics, crash logging, and PII-safe event
tracking to an API backend — no client-side JS, no separate dashboard service,
everything viewable straight from Django admin.

## Install

```bash
pip install django-uxlite
```

```python
# settings.py
INSTALLED_APPS = [
    ...,
    "uxlite",
]

MIDDLEWARE = [
    ...,
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # must come first
    "uxlite.middleware.UXLiteTrackingMiddleware",
]
```

```bash
python manage.py migrate uxlite
```

That's it — tracking, crash logging, and admin views are all live.

## What you get, out of the box

### 1. Every request logged automatically
`UXLiteTrackingMiddleware` records method, path, status code, response time,
IP, user agent, and the authenticated user (if any) for every request — into
`RequestLog`, visible in Django admin. Works under both WSGI and ASGI/async
views without forcing a sync thread-pool hop.

### 2. Sessions rolled up automatically
Requests and events from the same user (or same anonymous IP+user-agent) are
grouped into a `Session`, with a request count and last-seen timestamp — no
extra code needed.

### 3. Custom business events, with automatic PII masking
```python
from uxlite.tracking import track_event

track_event("checkout_completed", request=request, meta={"order_id": 42, "email": user.email})
```
Any key that looks sensitive (`password`, `token`, `email`, `card_number`,
`ssn`, etc. — configurable) is masked before it's ever written to the
database.

### 4. Crash logging, no extra code
Every unhandled exception is logged to `CrashLog` (type, message, traceback,
path, user) via Django's `got_request_exception` signal.

**Using Django REST Framework?** DRF catches most exceptions before Django
ever sees them, which would otherwise hide real 5xx failures from
`CrashLog`. Wire this in to close that gap:
```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "uxlite.exceptions.drf_exception_handler",
}
```

### 5. A user's full activity flow, in one click
In Django admin, click any user's name (from a Session, RequestLog, Event, or
CrashLog row) to open a merged, chronological timeline of everything that
user did — requests and custom events interleaved, e.g.:

```
POST /login/        200
GET  /orders/        200
checkout_completed   {order_id: 42, email: ***}
POST /pay/           200
```

### 6. Old data cleans itself up
```bash
python manage.py uxlite_purge
```
Deletes `RequestLog`/`Event`/`CrashLog` rows older than
`UXLITE_RETENTION_DAYS` (default 90 days), plus any now-empty sessions. Run
it on a schedule (cron, Celery beat, etc.).

## Configuration (all optional, all have defaults)

```python
UXLITE_SENSITIVE_FIELDS = ["password", "token", "secret", "email", "card_number", "ssn", "authorization"]
UXLITE_RETENTION_DAYS = 90
UXLITE_MASK_VALUE = "***"
UXLITE_TRACK_PATHS_EXCLUDE = ["/admin/", "/static/", "/media/", "/health/"]
UXLITE_SESSION_TIMEOUT_MINUTES = 30
```

## What it deliberately doesn't do

- No client-side JS, no pixel/DOM session replay
- No AI-generated insights
- No separate dashboard UI — Django admin is the UI

See [README.md](README.md) for the full setup reference.
