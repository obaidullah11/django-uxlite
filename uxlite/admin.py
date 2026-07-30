from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html

from .models import CrashLog, Event, RequestLog, Session
from .tracking import user_timeline


def _timeline_link(obj):
    user = obj.user
    if user is None:
        return "—"
    url = reverse("admin:uxlite_user_timeline", args=[user.pk])
    return format_html('<a href="{}">{}</a>', url, user)


_timeline_link.short_description = "user"


class UserTimelineAdminMixin:
    """Adds a "user/<id>/timeline/" admin view that shows a user's RequestLogs
    and Events merged into one chronological flow (login -> requests -> events)."""

    def get_urls(self):
        return [
            path(
                "user/<path:user_id>/timeline/",
                self.admin_site.admin_view(self.user_timeline_view),
                name="uxlite_user_timeline",
            ),
        ] + super().get_urls()

    def user_timeline_view(self, request, user_id):
        from django.contrib.auth import get_user_model
        from django.shortcuts import get_object_or_404, render

        user = get_object_or_404(get_user_model(), pk=user_id)
        context = {
            **self.admin_site.each_context(request),
            "title": f"Activity timeline for {user}",
            "user_obj": user,
            "timeline": user_timeline(user),
        }
        return render(request, "admin/uxlite/user_timeline.html", context)


@admin.register(Session)
class SessionAdmin(UserTimelineAdminMixin, admin.ModelAdmin):
    list_display = ("key", _timeline_link, "ip", "request_count", "started_at", "last_seen_at")
    list_filter = ("started_at",)
    search_fields = ("key", "user__username", "ip")
    ordering = ("-last_seen_at",)
    date_hierarchy = "last_seen_at"
    autocomplete_fields = ("user",)
    readonly_fields = ("key", "user", "ip", "started_at", "last_seen_at", "request_count")


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("method", "path", "status_code", "duration_ms", _timeline_link, "ip", "created_at")
    list_filter = ("method", "status_code", "created_at")
    search_fields = ("path", "user__username", "ip")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("user", "session")
    autocomplete_fields = ("user", "session")
    readonly_fields = [f.name for f in RequestLog._meta.fields]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", _timeline_link, "session", "created_at")
    list_filter = ("name", "created_at")
    search_fields = ("name", "user__username")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("user", "session")
    autocomplete_fields = ("user", "session")
    readonly_fields = [f.name for f in Event._meta.fields]


@admin.register(CrashLog)
class CrashLogAdmin(admin.ModelAdmin):
    list_display = ("exception_type", "path", _timeline_link, "created_at")
    list_filter = ("exception_type", "created_at")
    search_fields = ("exception_type", "message", "path", "user__username")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_select_related = ("user",)
    autocomplete_fields = ("user",)
    readonly_fields = [f.name for f in CrashLog._meta.fields]
