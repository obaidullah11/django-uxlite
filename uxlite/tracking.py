import hashlib

from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError, transaction
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
    try:
        with transaction.atomic():
            session, _created = Session.objects.update_or_create(
                key=key,
                defaults={"user": user, "ip": get_client_ip(request)},
            )
    except IntegrityError:
        # Another concurrent request won the race to create this key first.
        session = Session.objects.get(key=key)
    return session


def track_event(name, request=None, meta=None, user=None):
    """Record a custom business event. `meta` is masked before storage.
    Non-dict `meta` (e.g. a plain string) is wrapped under a "value" key, since
    JSONField requires an object and mask_payload only inspects dict/list keys."""
    session = get_or_create_session(request) if request is not None else None
    resolved_user = user
    if resolved_user is None and request is not None and request.user.is_authenticated:
        resolved_user = request.user

    meta = meta or {}
    if not isinstance(meta, dict):
        meta = {"value": meta}

    try:
        masked_meta = mask_payload(meta)
        DjangoJSONEncoder().encode(masked_meta)
    except (TypeError, ValueError):
        masked_meta = {"value": repr(meta)}

    return Event.objects.create(
        name=name,
        session=session,
        user=resolved_user,
        meta=masked_meta,
    )
