from django.test import RequestFactory, TestCase
from rest_framework.exceptions import APIException, ValidationError

from uxlite.exceptions import drf_exception_handler
from uxlite.models import CrashLog


class DRFExceptionHandlerTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _context(self):
        return {"request": self.factory.get("/api/whatever/"), "view": None, "args": (), "kwargs": {}}

    def test_logs_crash_for_5xx_api_exceptions(self):
        class ServerBug(APIException):
            status_code = 500
            default_detail = "boom"

        exc = ServerBug()
        try:
            raise exc
        except ServerBug:
            response = drf_exception_handler(exc, self._context())

        self.assertEqual(response.status_code, 500)
        self.assertEqual(CrashLog.objects.count(), 1)

    def test_does_not_log_crash_for_4xx_validation_errors(self):
        exc = ValidationError("bad input")
        try:
            raise exc
        except ValidationError:
            response = drf_exception_handler(exc, self._context())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(CrashLog.objects.count(), 0)
