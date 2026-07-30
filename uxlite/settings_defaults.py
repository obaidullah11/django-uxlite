from django.conf import settings

SENSITIVE_FIELDS = getattr(
    settings,
    "UXLITE_SENSITIVE_FIELDS",
    ["password", "token", "secret", "email", "card_number", "ssn", "authorization"],
)

RETENTION_DAYS = getattr(settings, "UXLITE_RETENTION_DAYS", 90)

MASK_VALUE = getattr(settings, "UXLITE_MASK_VALUE", "***")

TRACK_PATHS_EXCLUDE = getattr(
    settings,
    "UXLITE_TRACK_PATHS_EXCLUDE",
    ["/admin/", "/static/", "/media/", "/health/"],
)

SESSION_TIMEOUT_MINUTES = getattr(settings, "UXLITE_SESSION_TIMEOUT_MINUTES", 30)
