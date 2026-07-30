from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from uxlite.middleware import UXLiteTrackingMiddleware
from uxlite.models import RequestLog


class MiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="bob", password="pw"
        )

    def _make_middleware(self, status=200):
        def get_response(request):
            return HttpResponse(status=status)

        return UXLiteTrackingMiddleware(get_response)

    def test_logs_request(self):
        middleware = self._make_middleware(status=201)
        request = self.factory.post("/api/orders/")
        request.user = self.user

        middleware(request)

        self.assertEqual(RequestLog.objects.count(), 1)
        log = RequestLog.objects.first()
        self.assertEqual(log.method, "POST")
        self.assertEqual(log.status_code, 201)
        self.assertEqual(log.user, self.user)

    def test_excludes_configured_paths(self):
        middleware = self._make_middleware()
        request = self.factory.get("/admin/login/")
        request.user = self.user

        middleware(request)

        self.assertEqual(RequestLog.objects.count(), 0)

    async def test_logs_request_under_async_get_response(self):
        async def get_response(request):
            return HttpResponse(status=202)

        middleware = UXLiteTrackingMiddleware(get_response)
        self.assertTrue(middleware.async_mode)

        request = self.factory.post("/api/orders/")
        request.user = self.user

        await middleware(request)

        count = await RequestLog.objects.acount()
        self.assertEqual(count, 1)
