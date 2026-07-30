from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import resolve, reverse

from uxlite.admin import _timeline_link
from uxlite.models import RequestLog


class TimelineLinkTests(TestCase):
    def setUp(self):
        # Create a throwaway user first so self.user's PK diverges from the
        # RequestLog's own PK below -- otherwise both start at 1 and a
        # regression that links to the row's own PK could pass by accident.
        get_user_model().objects.create_user(username="decoy", password="pw")
        self.user = get_user_model().objects.create_user(
            username="alice", password="pw"
        )

    def _log(self, user=None):
        return RequestLog.objects.create(
            user=user,
            method="GET",
            path="/api/whatever/",
            status_code=200,
            duration_ms=5,
        )

    def test_links_to_the_related_users_pk_not_the_rows_own_pk(self):
        log = self._log(user=self.user)
        # Sanity check these differ, so the test would actually catch a
        # regression that links to the RequestLog's own PK instead.
        self.assertNotEqual(log.pk, self.user.pk)

        rendered = _timeline_link(log)

        expected_url = reverse("admin:uxlite_user_timeline", args=[self.user.pk])
        self.assertIn(expected_url, rendered)
        self.assertIn(str(self.user), rendered)

    def test_returns_placeholder_when_user_is_none(self):
        log = self._log(user=None)

        self.assertEqual(_timeline_link(log), "—")


class UserTimelineUrlTests(TestCase):
    def setUp(self):
        self.superuser = get_user_model().objects.create_superuser(
            username="root", password="pw", email="root@example.com"
        )

    def test_reverse_and_resolve_with_non_integer_pk(self):
        # Regression test: the URL used <int:user_id>, which 404s for any
        # non-integer PK (UUIDs, string PKs on custom user models, etc).
        url = reverse("admin:uxlite_user_timeline", args=["not-an-int-pk"])

        self.assertEqual(url, "/admin/uxlite/session/user/not-an-int-pk/timeline/")
        match = resolve(url)
        self.assertEqual(match.kwargs["user_id"], "not-an-int-pk")

    def test_timeline_view_renders_for_real_user(self):
        self.client = Client()
        self.client.force_login(self.superuser)

        url = reverse("admin:uxlite_user_timeline", args=[self.superuser.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
