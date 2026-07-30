import hashlib

from django.utils import timezone

from . import settings_defaults as cfg
from .masking import mask_payload
from .models import Event, Session


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _session_key_for(request):
    if request.user.is_authenticated:
        return f"user:{request.user.pk}"
    ip = get_client_ip(request) or "unknown"
    ua = request.META.get("HTTP_USER_AGENT", "")
    return "anon:" + hashlib.sha256(f"{ip}:{ua}".encode()).hexdigest()[:32]


def get_or_create_session(request):
    key = _session_key_for(request)
    cutoff = timezone.now() - timezone.timedelta(minutes=cfg.SESSION_TIMEOUT_MINUTES)

    session = (
        Session.objects.filter(key=key, last_seen_at__gte=cutoff).first()
    )
    if session:
        return session

    user = request.user if request.user.is_authenticated else None
    session, _created = Session.objects.update_or_create(
        key=key,
        defaults={"user": user, "ip": get_client_ip(request)},
    )
    return session


def track_event(name, request=None, meta=None, user=None):
    """Record a custom business event. `meta` is masked before storage."""
    session = get_or_create_session(request) if request is not None else None
    resolved_user = user
    if resolved_user is None and request is not None and request.user.is_authenticated:
        resolved_user = request.user

    return Event.objects.create(
        name=name,
        session=session,
        user=resolved_user,
        meta=mask_payload(meta or {}),
    )
