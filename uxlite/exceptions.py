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
