from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import resolve, reverse


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
