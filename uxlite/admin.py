from django.contrib import admin

from .models import CrashLog, Event, RequestLog, Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "ip", "request_count", "started_at", "last_seen_at")
    list_filter = ("started_at",)
    search_fields = ("key", "user__username", "ip")
    ordering = ("-last_seen_at",)
    date_hierarchy = "last_seen_at"
    autocomplete_fields = ("user",)
    readonly_fields = ("key", "user", "ip", "started_at", "last_seen_at", "request_count")


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("method", "path", "status_code", "duration_ms", "user", "ip", "created_at")
    list_filter = ("method", "status_code", "created_at")
    search_fields = ("path", "user__username", "ip")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("user", "session")
    autocomplete_fields = ("user", "session")
    readonly_fields = [f.name for f in RequestLog._meta.fields]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "session", "created_at")
    list_filter = ("name", "created_at")
    search_fields = ("name", "user__username")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("user", "session")
    autocomplete_fields = ("user", "session")
    readonly_fields = [f.name for f in Event._meta.fields]


@admin.register(CrashLog)
class CrashLogAdmin(admin.ModelAdmin):
    list_display = ("exception_type", "path", "user", "created_at")
    list_filter = ("exception_type", "created_at")
    search_fields = ("exception_type", "message", "path", "user__username")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("user",)
    autocomplete_fields = ("user",)
    readonly_fields = [f.name for f in CrashLog._meta.fields]
