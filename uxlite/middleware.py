import time

from django.db.models import F

from . import settings_defaults as cfg
from .models import RequestLog
from .tracking import get_client_ip, get_or_create_session


class UXLiteTrackingMiddleware:
    """Logs every request to RequestLog and rolls it up into a Session.
    Place after AuthenticationMiddleware so request.user is resolved."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_excluded(request.path):
            return self.get_response(request)

        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = int((time.monotonic() - start) * 1000)

        try:
            session = get_or_create_session(request)
            RequestLog.objects.create(
                session=session,
                user=request.user if request.user.is_authenticated else None,
                method=request.method,
                path=request.path[:512],
                status_code=response.status_code,
                duration_ms=duration_ms,
                ip=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
            )
            if session is not None:
                session.request_count = F("request_count") + 1
                session.save(update_fields=["request_count", "last_seen_at"])
        except Exception:
            # Tracking must never break the actual request/response cycle.
            pass

        return response

    @staticmethod
    def _is_excluded(path):
        return any(path.startswith(prefix) for prefix in cfg.TRACK_PATHS_EXCLUDE)
