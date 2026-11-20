import unittest
import uuid
import time

from db.mariadb import get_connection, add_rating
from db.mongodb import (
    setup_reviews_collection,
    get_reviews_collection,
    add_review,
    get_movie_reviews,
)
from screens.movie_details import get_community_reviews_with_ratings


class TestReviewSorting(unittest.TestCase):

    def setUp(self):
        setup_reviews_collection()

        self.movie_id = "s" + str(uuid.uuid4().int)[:8]
        self.user_ids = []

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
                        self.movie_id,
                        "Review Sorting Test",
                        "Test Director",
                        "Test Country",
                        "Temporary test movie"
                    )
                )

                for _ in range(4):
                    username = f"test_{uuid.uuid4().hex[:12]}"
                    cursor.execute(
                        "INSERT INTO users (username) VALUES (%s)",
                        (username,)
                    )
                    self.user_ids.append(cursor.lastrowid)

            connection.commit()

        finally:
            connection.close()

        self.user1, self.user2, self.user3, self.user4 = self.user_ids

        # Create reviews with different ratings.
        add_review(self.user1, self.movie_id, "First five-star review")
        add_rating(self.user1, self.movie_id, 5)

        time.sleep(0.02)

        add_review(self.user2, self.movie_id, "Second five-star review")
        add_rating(self.user2, self.movie_id, 5)

        add_review(self.user3, self.movie_id, "Three-star review")
        add_rating(self.user3, self.movie_id, 3)

        add_review(self.user4, self.movie_id, "Review without a rating")

    def tearDown(self):
        get_reviews_collection().delete_many({"movie_id": self.movie_id})

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM ratings WHERE movie_id = %s",
                    (self.movie_id,)
                )
                cursor.execute(
                    "DELETE FROM movies WHERE movie_id = %s",
                    (self.movie_id,)
                )
                for user_id in self.user_ids:
                    cursor.execute(
                        "DELETE FROM users WHERE user_id = %s",
                        (user_id,)
                    )
            connection.commit()
        finally:
            connection.close()

    def test_mongodb_retrieval_returns_review_documents_only(self):
        reviews = get_movie_reviews(self.movie_id, limit=10)

        self.assertEqual(len(reviews), 4)
        for review in reviews:
            self.assertNotIn("rating_stars", review)

    def test_highest_rated_reviews(self):
        reviews = get_community_reviews_with_ratings(
            self.movie_id,
            sort_by="highest_rated",
            limit=10
        )

        actual_order = [review["user_id"] for review in reviews]
        expected_order = [
            self.user2,
            self.user1,
            self.user3,
            self.user4,
        ]
        self.assertEqual(actual_order, expected_order)

    def test_rating_is_attached_by_streamlit_integration(self):
        reviews = get_community_reviews_with_ratings(
            self.movie_id,
            sort_by="highest_rated",
            limit=10
        )

        ratings = {
            review["user_id"]: review["rating_stars"]
            for review in reviews
        }
        self.assertEqual(ratings[self.user1], 5)
        self.assertEqual(ratings[self.user2], 5)
        self.assertEqual(ratings[self.user3], 3)
        self.assertIsNone(ratings[self.user4])

    def test_highest_rated_review_pagination(self):
        first_page = get_community_reviews_with_ratings(
            self.movie_id,
            sort_by="highest_rated",
            limit=2,
            offset=0
        )
        second_page = get_community_reviews_with_ratings(
            self.movie_id,
            sort_by="highest_rated",
            limit=2,
            offset=2
        )

        combined = first_page + second_page
        self.assertEqual(
            [review["user_id"] for review in combined],
            [self.user2, self.user1, self.user3, self.user4]
        )

    def test_newest_and_oldest_sorting_still_work(self):
        newest = get_community_reviews_with_ratings(
            self.movie_id,
            sort_by="newest",
            limit=10
        )
        oldest = get_community_reviews_with_ratings(
            self.movie_id,
            sort_by="oldest",
            limit=10
        )

        newest_order = [review["user_id"] for review in newest]
        oldest_order = [review["user_id"] for review in oldest]

        # The deliberate pause between the first two reviews makes their
        # relative order deterministic even if later inserts share a timestamp.
        self.assertLess(newest_order.index(self.user2), newest_order.index(self.user1))
        self.assertLess(oldest_order.index(self.user1), oldest_order.index(self.user2))

    def test_invalid_sort_option(self):
        with self.assertRaises(ValueError):
            get_movie_reviews(self.movie_id, sort_by="highest_rated")

        with self.assertRaises(ValueError):
            get_community_reviews_with_ratings(
                self.movie_id,
                sort_by="invalid"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
