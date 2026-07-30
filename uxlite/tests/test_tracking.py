from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from uxlite.models import Event, Session
from uxlite.tracking import get_or_create_session, track_event


class TrackingTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(
            username="alice", password="pw"
        )

    def _request(self, user=None):
        request = self.factory.get("/api/whatever/")
        request.user = user or AnonymousUser()
        return request

    def test_get_or_create_session_reuses_within_timeout(self):
        request = self._request(user=self.user)
        session1 = get_or_create_session(request)
        session2 = get_or_create_session(request)

        self.assertEqual(session1.pk, session2.pk)
        self.assertEqual(Session.objects.count(), 1)

    def test_track_event_masks_meta_and_links_session(self):
        request = self._request(user=self.user)
        event = track_event("checkout_completed", request=request, meta={"email": "a@b.com"})

        self.assertEqual(Event.objects.count(), 1)
        self.assertNotEqual(event.meta["email"], "a@b.com")
        self.assertEqual(event.session.user, self.user)
        self.assertEqual(event.user, self.user)
