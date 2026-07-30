from django.contrib import admin

from .models import CrashLog, Event, RequestLog, Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "ip", "request_count", "started_at", "last_seen_at")
    list_filter = ("started_at",)
    search_fields = ("key", "user__username", "ip")
    ordering = ("-last_seen_at",)


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("method", "path", "status_code", "duration_ms", "user", "ip", "created_at")
    list_filter = ("method", "status_code", "created_at")
    search_fields = ("path", "user__username", "ip")
    ordering = ("-created_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "session", "created_at")
    list_filter = ("name", "created_at")
    search_fields = ("name", "user__username")
    ordering = ("-created_at",)


@admin.register(CrashLog)
class CrashLogAdmin(admin.ModelAdmin):
    list_display = ("exception_type", "path", "user", "created_at")
    list_filter = ("exception_type", "created_at")
    search_fields = ("exception_type", "message", "path", "user__username")
    ordering = ("-created_at",)
