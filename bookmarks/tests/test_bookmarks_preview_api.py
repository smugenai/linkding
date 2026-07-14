from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from bookmarks.tests.helpers import BookmarkFactoryMixin, LinkdingApiTestCase


class BookmarksPreviewApiTestCase(LinkdingApiTestCase, BookmarkFactoryMixin):
    def authenticate(self):
        self.api_token = self.setup_api_token()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.api_token.key)

    def test_preview_returns_status_and_body(self):
        self.authenticate()

        class FakeResponse:
            status_code = 200
            headers = {"Content-Type": "text/html; charset=utf-8"}
            text = "<html><title>Hello</title></html>"

        with patch("requests.get", return_value=FakeResponse()):
            response = self.get(
                reverse("linkding:bookmark-preview") + "?url=https://example.com",
                expected_status_code=status.HTTP_200_OK,
            )

        self.assertEqual(response.data["status_code"], 200)
        self.assertIn("Hello", response.data["body"])

    def test_preview_requires_url(self):
        self.authenticate()

        self.get(
            reverse("linkding:bookmark-preview"),
            expected_status_code=status.HTTP_400_BAD_REQUEST,
        )
