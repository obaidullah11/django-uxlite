from django.core.management.base import BaseCommand
from django.utils import timezone

from ... import settings_defaults as cfg
from ...models import CrashLog, Event, RequestLog, Session


class Command(BaseCommand):
    help = "Delete uxlite analytics/crash records older than UXLITE_RETENTION_DAYS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Override UXLITE_RETENTION_DAYS for this run.",
        )

    def handle(self, *args, **options):
        days = options["days"] if options["days"] is not None else cfg.RETENTION_DAYS
        cutoff = timezone.now() - timezone.timedelta(days=days)

        requests_deleted, _ = RequestLog.objects.filter(created_at__lt=cutoff).delete()
        events_deleted, _ = Event.objects.filter(created_at__lt=cutoff).delete()
        crashes_deleted, _ = CrashLog.objects.filter(created_at__lt=cutoff).delete()
        sessions_deleted, _ = Session.objects.filter(
            requests__isnull=True, events__isnull=True
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Purged (older than {days}d): "
                f"{requests_deleted} requests, {events_deleted} events, "
                f"{crashes_deleted} crashes, {sessions_deleted} empty sessions."
            )
        )
