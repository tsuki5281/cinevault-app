
import unittest
import uuid

from db.mariadb import (
    get_connection,
    add_rating,
    get_rating,
    update_rating,
    delete_rating,
    get_average_rating,
    get_rating_count,
    get_highest_rated_movies,
    add_to_watchlist,
    get_watchlist,
    remove_from_watchlist,
)


class TestRatingsWatchlist(unittest.TestCase):

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
        """Remove only the temporary test users and their records."""
        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for user_id in self.user_ids:
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

    # -------------------------
    # Ratings CRUD Tests
    # -------------------------

    def test_add_and_get_rating(self):
        self.assertTrue(
            add_rating(self.user1, self.movie_id, 4)
        )

        result = get_rating(self.user1, self.movie_id)

        self.assertIsNotNone(result)
        self.assertEqual(result["stars"], 4)

    def test_update_rating(self):
        add_rating(self.user1, self.movie_id, 3)

        self.assertTrue(
            update_rating(self.user1, self.movie_id, 5)
        )

        result = get_rating(self.user1, self.movie_id)

        self.assertEqual(result["stars"], 5)

    def test_delete_rating(self):
        add_rating(self.user1, self.movie_id, 4)

        self.assertTrue(
            delete_rating(self.user1, self.movie_id)
        )

        self.assertIsNone(
            get_rating(self.user1, self.movie_id)
        )

    def test_duplicate_rating(self):
        self.assertTrue(
            add_rating(self.user1, self.movie_id, 4)
        )

        self.assertFalse(
            add_rating(self.user1, self.movie_id, 5)
        )

    def test_invalid_rating_values(self):
        for stars in [0, 6, -1, 2.5, "4"]:
            with self.subTest(stars=stars):
                with self.assertRaises(ValueError):
                    add_rating(
                        self.user1,
                        self.movie_id,
                        stars
                    )

    def test_invalid_user_and_movie_ids(self):
        with self.assertRaises(ValueError):
            add_rating(99999999, self.movie_id, 4)

        with self.assertRaises(ValueError):
            add_rating(self.user1, "badmovie", 4)

    def test_update_missing_rating(self):
        self.assertFalse(
            update_rating(self.user1, self.movie_id, 4)
        )

    def test_delete_missing_rating(self):
        self.assertFalse(
            delete_rating(self.user1, self.movie_id)
        )

    # -------------------------
    # Rating Summary Tests
    # -------------------------

    def test_rating_average_and_count(self):
        initial_count = get_rating_count(self.movie_id)
        initial_average = get_average_rating(self.movie_id)

        initial_total = (
            float(initial_average) * initial_count
            if initial_average is not None
            else 0
        )

        add_rating(self.user1, self.movie_id, 4)
        add_rating(self.user2, self.movie_id, 5)

        expected_count = initial_count + 2
        expected_average = (
            initial_total + 4 + 5
        ) / expected_count

        self.assertEqual(
            get_rating_count(self.movie_id),
            expected_count
        )

        self.assertAlmostEqual(
            float(get_average_rating(self.movie_id)),
            expected_average,
            places=4
        )

    def test_highest_rated_movies(self):
        add_rating(self.user1, self.movie_id, 4)
        add_rating(self.user2, self.movie_id, 5)

        results = get_highest_rated_movies(
            minimum_ratings=2,
            limit=10000
        )

        movie_ids = [movie["movie_id"] for movie in results]

        self.assertIn(self.movie_id, movie_ids)

    def test_invalid_summary_parameters(self):
        for minimum_ratings in [0, -1, 1.5, "2"]:
            with self.subTest(minimum_ratings=minimum_ratings):
                with self.assertRaises(ValueError):
                    get_highest_rated_movies(
                        minimum_ratings=minimum_ratings
                    )

        for limit in [0, -1, 1.5, "10"]:
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    get_highest_rated_movies(limit=limit)

    # -------------------------
    # Watchlist CRUD Tests
    # -------------------------

    def test_add_and_get_watchlist(self):
        self.assertTrue(
            add_to_watchlist(self.user1, self.movie_id)
        )

        result = get_watchlist(self.user1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["movie_id"], self.movie_id)

    def test_duplicate_watchlist_entry(self):
        self.assertTrue(
            add_to_watchlist(self.user1, self.movie_id)
        )

        self.assertFalse(
            add_to_watchlist(self.user1, self.movie_id)
        )

    def test_remove_from_watchlist(self):
        add_to_watchlist(self.user1, self.movie_id)

        self.assertTrue(
            remove_from_watchlist(self.user1, self.movie_id)
        )

        self.assertEqual(
            get_watchlist(self.user1),
            []
        )

    def test_invalid_watchlist_ids(self):
        with self.assertRaises(ValueError):
            add_to_watchlist(99999999, self.movie_id)

        with self.assertRaises(ValueError):
            add_to_watchlist(self.user1, "badmovie")

    def test_remove_missing_watchlist_entry(self):
        self.assertFalse(
            remove_from_watchlist(self.user1, self.movie_id)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
