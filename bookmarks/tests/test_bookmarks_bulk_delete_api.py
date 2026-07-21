from django.urls import reverse
from rest_framework import status

from bookmarks.models import Bookmark
from bookmarks.tests.helpers import BookmarkFactoryMixin, LinkdingApiTestCase


class BookmarksBulkDeleteApiTestCase(LinkdingApiTestCase, BookmarkFactoryMixin):
    def authenticate(self):
        self.api_token = self.setup_api_token()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.api_token.key)

    def test_bulk_delete_removes_own_bookmarks(self):
        self.authenticate()
        b1 = self.setup_bookmark()
        b2 = self.setup_bookmark()
        b3 = self.setup_bookmark()

        response = self.client.post(
            reverse("linkding:bookmark-bulk-delete"),
            {"bookmark_ids": [b1.id, b2.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Bookmark.objects.filter(id__in=[b1.id, b2.id]).exists())
        self.assertTrue(Bookmark.objects.filter(id=b3.id).exists())

    def test_bulk_delete_ignores_other_users_bookmarks(self):
        self.authenticate()
        other_user = self.setup_user()
        theirs = self.setup_bookmark(user=other_user)

        response = self.client.post(
            reverse("linkding:bookmark-bulk-delete"),
            {"bookmark_ids": [theirs.id]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Bookmark.objects.filter(id=theirs.id).exists())

    def test_bulk_delete_with_empty_list_is_noop(self):
        self.authenticate()
        b1 = self.setup_bookmark()

        response = self.client.post(
            reverse("linkding:bookmark-bulk-delete"),
            {"bookmark_ids": []},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Bookmark.objects.filter(id=b1.id).exists())
