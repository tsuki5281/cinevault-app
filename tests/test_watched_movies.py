
import unittest
import uuid

from db.mariadb import (
    get_connection,
    mark_as_watched,
    get_watched_movies,
    remove_watched_status,
)


class TestWatchedMovies(unittest.TestCase):

    def setUp(self):
        """Create temporary users for each test."""
        self.movie_id = "s10"
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
        """Remove temporary users and their watched records."""
        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for user_id in self.user_ids:
                    cursor.execute(
                        "DELETE FROM watched_movies WHERE user_id = %s",
                        (user_id,)
                    )

                    cursor.execute(
                        "DELETE FROM ratings WHERE user_id = %s",
                        (user_id,)
                    )

                    cursor.execute(
                        "DELETE FROM watchlist WHERE user_id = %s",
                        (user_id,)
                    )

                    cursor.execute(
                        "DELETE FROM users WHERE user_id = %s",
                        (user_id,)
                    )

            connection.commit()

        finally:
            connection.close()

    # Watched Movies CRUD Tests

    def test_mark_and_get_watched_movie(self):
        self.assertTrue(
            mark_as_watched(self.user1, self.movie_id)
        )

        result = get_watched_movies(self.user1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["movie_id"], self.movie_id)
        self.assertEqual(result[0]["title"], "1920")
        self.assertIsNotNone(result[0]["watched_at"])

    def test_duplicate_watched_movie(self):
        self.assertTrue(
            mark_as_watched(self.user1, self.movie_id)
        )

        self.assertFalse(
            mark_as_watched(self.user1, self.movie_id)
        )

    def test_remove_watched_status(self):
        mark_as_watched(self.user1, self.movie_id)

        self.assertTrue(
            remove_watched_status(self.user1, self.movie_id)
        )

        self.assertEqual(
            get_watched_movies(self.user1),
            []
        )

    def test_remove_missing_watched_movie(self):
        self.assertFalse(
            remove_watched_status(self.user1, self.movie_id)
        )

    def test_invalid_user_and_movie_ids(self):
        with self.assertRaises(ValueError):
            mark_as_watched(99999999, self.movie_id)

        with self.assertRaises(ValueError):
            mark_as_watched(self.user1, "badmovie")

    def test_watched_movies_are_user_specific(self):
        mark_as_watched(self.user1, self.movie_id)

        self.assertEqual(
            get_watched_movies(self.user2),
            []
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
