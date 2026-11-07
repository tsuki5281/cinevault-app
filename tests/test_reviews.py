
import unittest
import uuid

from pymongo.errors import WriteError

from db.mariadb import get_connection
from db.mongodb import (
    get_reviews_collection,
    setup_reviews_collection,
    add_review,
    get_review,
    update_review,
    delete_review,
    get_movie_reviews,
    get_user_reviews,
    get_review_count,
)


class TestReviews(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_reviews_collection()

    def setUp(self):
        """Create temporary users for each test."""
        self.movie_id = "s10"
        self.other_movie_id = "s2"
        self.user_ids = []

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for _ in range(2):
                    username = f"test_{uuid.uuid4().hex[:12]}"

                    cursor.execute(
                        "INSERT INTO users (username) VALUES (%s)",
                        (username,)
                    )

                    self.user_ids.append(cursor.lastrowid)

            connection.commit()

        finally:
            connection.close()

        self.user1, self.user2 = self.user_ids

    def tearDown(self):
        """Remove only the temporary test users and their reviews."""
        get_reviews_collection().delete_many({"user_id": {"$in": self.user_ids}})

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for user_id in self.user_ids:
                    cursor.execute(
                        "DELETE FROM users WHERE user_id = %s",
                        (user_id,)
                    )

            connection.commit()

        finally:
            connection.close()

    # -------------------------
    # Reviews CRUD Tests
    # -------------------------

    def test_add_and_get_review(self):
        self.assertTrue(
            add_review(self.user1, self.movie_id, "Great movie!", tags=["Acting", "acting", " story "])
        )

        review = get_review(self.user1, self.movie_id)

        self.assertEqual(review["review_text"], "Great movie!")
        self.assertEqual(review["tags"], ["acting", "story"])
        self.assertFalse(review["spoiler"])
        self.assertIn("created_at", review)

    def test_duplicate_review_returns_false(self):
        self.assertTrue(add_review(self.user1, self.movie_id, "First review"))
        self.assertFalse(add_review(self.user1, self.movie_id, "Second review"))

    def test_invalid_user_or_movie_raises(self):
        with self.assertRaises(ValueError):
            add_review(999999999, self.movie_id, "No such user")

        with self.assertRaises(ValueError):
            add_review(self.user1, "s999999", "No such movie")

    def test_invalid_input_raises(self):
        with self.assertRaises(ValueError):
            add_review(self.user1, self.movie_id, "   ")

        with self.assertRaises(ValueError):
            add_review(self.user1, self.movie_id, "x" * 2001)

        with self.assertRaises(ValueError):
            add_review(self.user1, self.movie_id, "Bad spoiler", spoiler="yes")

        with self.assertRaises(ValueError):
            add_review("1", self.movie_id, "User ID as string")

    def test_get_missing_review_returns_none(self):
        self.assertIsNone(get_review(self.user1, self.movie_id))

    def test_update_review(self):
        add_review(self.user1, self.movie_id, "Original text")

        self.assertTrue(
            update_review(self.user1, self.movie_id, review_text="Edited text", spoiler=True)
        )

        review = get_review(self.user1, self.movie_id)

        self.assertEqual(review["review_text"], "Edited text")
        self.assertTrue(review["spoiler"])
        self.assertIn("updated_at", review)

    def test_other_user_cannot_update_or_delete(self):
        add_review(self.user1, self.movie_id, "User 1's review")

        self.assertFalse(update_review(self.user2, self.movie_id, review_text="Hacked"))
        self.assertFalse(delete_review(self.user2, self.movie_id))

        self.assertEqual(get_review(self.user1, self.movie_id)["review_text"], "User 1's review")

    def test_update_with_nothing_raises(self):
        add_review(self.user1, self.movie_id, "Some text")

        with self.assertRaises(ValueError):
            update_review(self.user1, self.movie_id)

    def test_delete_review(self):
        add_review(self.user1, self.movie_id, "To be deleted")

        self.assertTrue(delete_review(self.user1, self.movie_id))
        self.assertIsNone(get_review(self.user1, self.movie_id))
        self.assertFalse(delete_review(self.user1, self.movie_id))

    # -------------------------
    # Browsing Tests
    # -------------------------

    def test_movie_reviews_hide_spoilers_and_tag(self):
        add_review(self.user1, self.movie_id, "Spoiler review", spoiler=True, tags=["ending"])
        add_review(self.user2, self.movie_id, "Safe review", tags=["acting"])

        texts = []
        for review in get_movie_reviews(self.movie_id, hide_spoilers=True, limit=100):
            texts.append(review["review_text"])
        self.assertIn("Safe review", texts)
        self.assertNotIn("Spoiler review", texts)

        texts = []
        for review in get_movie_reviews(self.movie_id, tag="ENDING", limit=100):
            texts.append(review["review_text"])
        self.assertIn("Spoiler review", texts)
        self.assertNotIn("Safe review", texts)

    def test_user_reviews_and_count(self):
        before = get_review_count(self.movie_id)

        add_review(self.user1, self.movie_id, "Review A")
        add_review(self.user1, self.other_movie_id, "Review B")

        self.assertEqual(len(get_user_reviews(self.user1)), 2)
        self.assertEqual(get_review_count(self.movie_id), before + 1)

    def test_invalid_browse_parameters_raise(self):
        with self.assertRaises(ValueError):
            get_movie_reviews(self.movie_id, sort_by="best")

        with self.assertRaises(ValueError):
            get_movie_reviews(self.movie_id, limit=0)

        with self.assertRaises(ValueError):
            get_movie_reviews(self.movie_id, offset=-1)

    # -------------------------
    # Database-level validation ($jsonSchema)
    # -------------------------

    def test_database_rejects_invalid_document(self):
        """Even code that skips add_review cannot store a bad review."""
        with self.assertRaises(WriteError):
            get_reviews_collection().insert_one({
                "user_id": self.user1,
                "movie_id": "not-a-movie-id",
                "review_text": "",
                "spoiler": "no",
                "tags": [],
            })


if __name__ == "__main__":
    unittest.main()
