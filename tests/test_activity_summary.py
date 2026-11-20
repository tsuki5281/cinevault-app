
import unittest
import uuid

from db.mariadb import (
    get_connection,
    add_rating,
    add_to_watchlist,
    mark_as_watched
)
from db.mongodb import (
    setup_reviews_collection,
    get_reviews_collection,
    add_review
)
from db.activity import get_user_activity_summary


class TestActivitySummary(unittest.TestCase):

    def setUp(self):
        setup_reviews_collection()

        self.username = "test_summary_" + uuid.uuid4().hex[:10]

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username) VALUES (%s)",
                    (self.username,)
                )
                self.user_id = cursor.lastrowid

            connection.commit()

        finally:
            connection.close()

    def tearDown(self):
        get_reviews_collection().delete_many(
            {"user_id": self.user_id}
        )

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM ratings WHERE user_id = %s",
                    (self.user_id,)
                )

                cursor.execute(
                    "DELETE FROM watchlist WHERE user_id = %s",
                    (self.user_id,)
                )

                cursor.execute(
                    "DELETE FROM watched_movies WHERE user_id = %s",
                    (self.user_id,)
                )

                cursor.execute(
                    "DELETE FROM users WHERE user_id = %s",
                    (self.user_id,)
                )

            connection.commit()

        finally:
            connection.close()

    def test_activity_counts(self):
        add_rating(self.user_id, "s101", 5)
        add_to_watchlist(self.user_id, "s28")
        mark_as_watched(self.user_id, "s107")

        add_review(
            self.user_id,
            "s101",
            "Excellent movie."
        )

        add_review(
            self.user_id,
            "s28",
            "Interesting movie."
        )

        summary = get_user_activity_summary(self.user_id)

        self.assertEqual(summary["movies_rated"], 1)
        self.assertEqual(summary["reviews_written"], 2)
        self.assertEqual(summary["movies_watched"], 1)
        self.assertEqual(summary["watchlist_items"], 1)

    def test_new_user_has_zero_activity(self):
        summary = get_user_activity_summary(self.user_id)

        self.assertEqual(summary["movies_rated"], 0)
        self.assertEqual(summary["reviews_written"], 0)
        self.assertEqual(summary["movies_watched"], 0)
        self.assertEqual(summary["watchlist_items"], 0)

    def test_invalid_user_id(self):
        for user_id in [0, -1, True, "1"]:
            with self.subTest(user_id=user_id):
                with self.assertRaises(ValueError):
                    get_user_activity_summary(user_id)


if __name__ == "__main__":
    unittest.main()
