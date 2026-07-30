import traceback as tb_module

from django.core.signals import got_request_exception
from django.dispatch import receiver

from .models import CrashLog


@receiver(got_request_exception)
def log_crash(sender, request=None, **kwargs):
    import sys

    exc_type, exc_value, exc_tb = sys.exc_info()
    if exc_type is None:
        return

    user = None
    path = ""
    if request is not None:
        path = request.path[:512]
        if getattr(request, "user", None) is not None and request.user.is_authenticated:
            user = request.user

    _log_crash(exc_type, exc_value, exc_tb, path=path, user=user)


def _log_crash(exc_type, exc_value, exc_tb, path="", user=None):
    try:
        CrashLog.objects.create(
            exception_type=exc_type.__name__,
            message=str(exc_value)[:5000],
            traceback="".join(tb_module.format_exception(exc_type, exc_value, exc_tb))[:20000],
            path=path,
            user=user,
        )
    except Exception:
        # Crash logging must never raise inside exception handling itself.
        pass


def drf_exception_handler(exc, context):
    """Exceptions DRF doesn't recognize (e.g. plain bugs) fall through to Django's
    got_request_exception signal as usual. But DRF-recognized exceptions that still
    resolve to a 5xx response (e.g. a custom APIException marking a real server
    failure) are swallowed by DRF before that signal ever fires. Wire this up in
    DRF's settings to log those too:

        REST_FRAMEWORK = {"EXCEPTION_HANDLER": "uxlite.exceptions.drf_exception_handler"}
    """
    from rest_framework.views import exception_handler as drf_default_handler

    response = drf_default_handler(exc, context)

    if response is not None and response.status_code >= 500:
        request = context.get("request")
        path = request.path[:512] if request is not None else ""
        user = None
        if (
            request is not None
            and getattr(request, "user", None) is not None
            and request.user.is_authenticated
        ):
            user = request.user
        _log_crash(type(exc), exc, exc.__traceback__, path=path, user=user)

    return response
