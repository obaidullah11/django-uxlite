from django.conf import settings
from django.db import models


class Session(models.Model):
    key = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    request_count = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["last_seen_at"])]

    def __str__(self):
        return f"Session({self.key})"


class RequestLog(models.Model):
    session = models.ForeignKey(
        Session, null=True, blank=True, on_delete=models.SET_NULL, related_name="requests"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=512, db_index=True)
    status_code = models.PositiveSmallIntegerField()
    duration_ms = models.PositiveIntegerField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{self.method} {self.path} [{self.status_code}]"


class Event(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    session = models.ForeignKey(
        Session, null=True, blank=True, on_delete=models.SET_NULL, related_name="events"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return self.name


class CrashLog(models.Model):
    exception_type = models.CharField(max_length=255)
    message = models.TextField(blank=True, default="")
    traceback = models.TextField(blank=True, default="")
    path = models.CharField(max_length=512, blank=True, default="")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["created_at"])]

    def __str__(self):
        return f"{self.exception_type} @ {self.path}"
