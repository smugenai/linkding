import csv
import io

from django.urls import reverse
from rest_framework import status

from bookmarks.tests.helpers import BookmarkFactoryMixin, LinkdingApiTestCase


class TagsExportApiTestCase(LinkdingApiTestCase, BookmarkFactoryMixin):
    def authenticate(self):
        self.api_token = self.setup_api_token()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.api_token.key)

    def _read_csv(self, response):
        reader = csv.reader(io.StringIO(response.content.decode("utf-8")))
        return list(reader)

    def test_export_returns_csv_for_owner_only(self):
        self.authenticate()
        other_user = self.setup_user()
        my_tag = self.setup_tag(name="alpha")
        their_tag = self.setup_tag(user=other_user, name="beta")

        response = self.get(
            reverse("linkding:tag-export"),
            expected_status_code=status.HTTP_200_OK,
        )

        self.assertEqual(response["Content-Type"], "text/csv")
        rows = self._read_csv(response)
        self.assertEqual(rows[0], ["id", "name", "date_added", "bookmark_count"])
        names = [row[1] for row in rows[1:]]
        self.assertIn(my_tag.name, names)
        self.assertNotIn(their_tag.name, names)

    def test_export_counts_bookmarks(self):
        self.authenticate()
        tag = self.setup_tag(name="counted")
        self.setup_bookmark(tags=[tag])
        self.setup_bookmark(tags=[tag])

        response = self.get(
            reverse("linkding:tag-export"),
            expected_status_code=status.HTTP_200_OK,
        )
        rows = self._read_csv(response)
        row_for_tag = next(r for r in rows[1:] if r[1] == "counted")
        self.assertEqual(row_for_tag[3], "2")

    def test_export_requires_authentication(self):
        self.get(
            reverse("linkding:tag-export"),
            expected_status_code=status.HTTP_401_UNAUTHORIZED,
        )
