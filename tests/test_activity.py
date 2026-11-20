
import unittest
import uuid

from db.mariadb import get_connection, add_rating
from db.mongodb import (
    setup_reviews_collection,
    get_reviews_collection,
    add_review
)
from db.activity import get_user_contributions


class TestUserContributions(unittest.TestCase):

    def setUp(self):
        setup_reviews_collection()

        self.username = "test_activity_" + uuid.uuid4().hex[:10]
        self.movie_ids = []

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

        self.both_movie = self.create_movie("Both Contributions")
        self.review_movie = self.create_movie("Review Only")
        self.rating_movie = self.create_movie("Rating Only")

        add_rating(self.user_id, self.both_movie, 5)
        add_review(
            self.user_id,
            self.both_movie,
            "An excellent movie.",
            tags=["test-tag"]
        )

        add_review(
            self.user_id,
            self.review_movie,
            "A review without a rating."
        )

        add_rating(self.user_id, self.rating_movie, 4)

    def create_movie(self, title):
        movie_id = "s" + str(uuid.uuid4().int)[:8]

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO movies
                        (movie_id, title, director, country, description)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        movie_id,
                        "CVTEST " + title,
                        "Test Director",
                        "Singapore",
                        "Temporary test movie"
                    )
                )

            connection.commit()

        finally:
            connection.close()

        self.movie_ids.append(movie_id)

        return movie_id

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

                for movie_id in self.movie_ids:
                    cursor.execute(
                        "DELETE FROM movies WHERE movie_id = %s",
                        (movie_id,)
                    )

                cursor.execute(
                    "DELETE FROM users WHERE user_id = %s",
                    (self.user_id,)
                )

            connection.commit()

        finally:
            connection.close()

    def test_combines_rating_and_review(self):
        results = get_user_contributions(self.user_id)

        both_entry = next(
            entry for entry in results
            if entry["movie_id"] == self.both_movie
        )

        self.assertEqual(both_entry["rating_stars"], 5)
        self.assertEqual(
            both_entry["review_text"],
            "An excellent movie."
        )

    def test_review_only_movie(self):
        results = get_user_contributions(self.user_id)

        entry = next(
            entry for entry in results
            if entry["movie_id"] == self.review_movie
        )

        self.assertIsNone(entry["rating_stars"])
        self.assertEqual(
            entry["review_text"],
            "A review without a rating."
        )

    def test_rating_only_movie(self):
        results = get_user_contributions(self.user_id)

        entry = next(
            entry for entry in results
            if entry["movie_id"] == self.rating_movie
        )

        self.assertEqual(entry["rating_stars"], 4)
        self.assertIsNone(entry["review_text"])

    def test_each_movie_appears_only_once(self):
        results = get_user_contributions(self.user_id)

        movie_ids = [
            entry["movie_id"]
            for entry in results
        ]

        self.assertEqual(len(movie_ids), len(set(movie_ids)))
        self.assertEqual(len(results), 3)

    def test_activity_is_sorted_by_latest_contribution(self):
        results = get_user_contributions(self.user_id)

        dates = [
            entry["last_activity_at"]
            for entry in results
        ]

        self.assertEqual(
            dates,
            sorted(dates, reverse=True)
        )

    def test_review_pagination(self):
        for i in range(19):
            movie_id = self.create_movie("Pagination " + str(i))

            add_review(
                self.user_id,
                movie_id,
                "Temporary pagination review."
            )

        results = get_user_contributions(self.user_id)

        review_count = sum(
            entry["review_text"] is not None
            for entry in results
        )

        self.assertEqual(review_count, 21)
        self.assertEqual(len(results), 22)

    def test_invalid_user_id(self):
        for user_id in [0, -1, True, "1"]:
            with self.subTest(user_id=user_id):
                with self.assertRaises(ValueError):
                    get_user_contributions(user_id)


if __name__ == "__main__":
    unittest.main()
