from django.apps import AppConfig


class UXLiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "uxlite"
    verbose_name = "UXLite Analytics"

    def ready(self):
        from . import exceptions  # noqa: F401  (registers signal receiver)
