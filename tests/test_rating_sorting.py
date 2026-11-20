
import unittest
import uuid

from db.mariadb import (
    get_connection,
    add_rating,
    get_movie_rating_summaries,
    get_movie_user_ratings,
    get_movies_sorted_by_rating,
)
from db.catalogue import browse_movies


class TestRatingSorting(unittest.TestCase):

    def setUp(self):
        self.movie_ids = [
            "t" + uuid.uuid4().hex[:7]
            for _ in range(4)
        ]

        self.user_ids = []

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for i in range(4):
                    username = f"test_{uuid.uuid4().hex[:12]}"

                    cursor.execute(
                        "INSERT INTO users (username) VALUES (%s)",
                        (username,)
                    )
                    self.user_ids.append(cursor.lastrowid)

                movies = [
                    ("CVTEST High Average", self.movie_ids[0]),
                    ("CVTEST More Ratings", self.movie_ids[1]),
                    ("CVTEST Fewer Ratings", self.movie_ids[2]),
                    ("CVTEST No Ratings", self.movie_ids[3]),
                ]

                for title, movie_id in movies:
                    cursor.execute(
                        """
                        INSERT INTO movies
                        (movie_id, title, director, country, description)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (movie_id, title, "Test Director", "Test Country", "Test movie")
                    )

            connection.commit()

        finally:
            connection.close()

        # Create ratings with different averages and counts.
        add_rating(self.user_ids[0], self.movie_ids[0], 5)
        add_rating(self.user_ids[1], self.movie_ids[0], 5)

        add_rating(self.user_ids[0], self.movie_ids[1], 4)
        add_rating(self.user_ids[1], self.movie_ids[1], 4)

        add_rating(self.user_ids[2], self.movie_ids[2], 4)

    def tearDown(self):
        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                placeholders = ", ".join(["%s"] * len(self.movie_ids))

                cursor.execute(
                    f"DELETE FROM ratings WHERE movie_id IN ({placeholders})",
                    self.movie_ids
                )

                cursor.execute(
                    f"DELETE FROM movies WHERE movie_id IN ({placeholders})",
                    self.movie_ids
                )

                for user_id in self.user_ids:
                    cursor.execute(
                        "DELETE FROM users WHERE user_id = %s",
                        (user_id,)
                    )

            connection.commit()

        finally:
            connection.close()


    def test_movie_rating_summaries(self):
        summaries = get_movie_rating_summaries(self.movie_ids)

        self.assertEqual(
            summaries[self.movie_ids[0]]["rating_count"],
            2
        )
        self.assertAlmostEqual(
            float(summaries[self.movie_ids[0]]["average_rating"]),
            5.0
        )

        self.assertEqual(
            summaries[self.movie_ids[1]]["rating_count"],
            2
        )
        self.assertAlmostEqual(
            float(summaries[self.movie_ids[1]]["average_rating"]),
            4.0
        )

        self.assertEqual(
            summaries[self.movie_ids[2]]["rating_count"],
            1
        )
        self.assertAlmostEqual(
            float(summaries[self.movie_ids[2]]["average_rating"]),
            4.0
        )

        self.assertIsNone(
            summaries[self.movie_ids[3]]["average_rating"]
        )
        self.assertEqual(
            summaries[self.movie_ids[3]]["rating_count"],
            0
        )

    def test_movie_user_ratings(self):
        ratings = get_movie_user_ratings(
            self.movie_ids[0],
            self.user_ids
        )

        self.assertEqual(
            ratings,
            {
                self.user_ids[0]: 5,
                self.user_ids[1]: 5
            }
        )

    def test_rating_helpers_return_empty_results_for_empty_ids(self):
        self.assertEqual(get_movie_rating_summaries([]), {})
        self.assertEqual(
            get_movie_user_ratings(self.movie_ids[0], []),
            {}
        )

    def test_highest_rated_sorting(self):
        results = get_movies_sorted_by_rating(self.movie_ids)

        actual_order = [movie["movie_id"] for movie in results]
        expected_order = [
            self.movie_ids[0],
            self.movie_ids[1],
            self.movie_ids[2],
            self.movie_ids[3],
        ]

        self.assertEqual(actual_order, expected_order)
        self.assertEqual(results[-1]["rating_count"], 0)
        self.assertIsNone(results[-1]["average_rating"])

    def test_rating_sorting_pagination(self):
        all_results = get_movies_sorted_by_rating(self.movie_ids)
        first_page = all_results[:2]
        second_page = all_results[2:4]

        self.assertEqual(len(first_page), 2)
        self.assertEqual(len(second_page), 2)
        self.assertEqual(
            [movie["movie_id"] for movie in first_page],
            self.movie_ids[:2]
        )
        self.assertEqual(
            [movie["movie_id"] for movie in second_page],
            self.movie_ids[2:]
        )

    def test_catalogue_can_return_all_filtered_matches(self):
        results = browse_movies(title="CVTEST", limit=None)

        self.assertEqual(len(results), 4)
        self.assertEqual(
            {movie["movie_id"] for movie in results},
            set(self.movie_ids)
        )

    def test_rating_sorting_is_not_a_catalogue_sort_option(self):
        with self.assertRaises(ValueError):
            browse_movies(sort_by="rating_desc")

    def test_empty_rating_sort_input(self):
        self.assertEqual(get_movies_sorted_by_rating([]), [])

    def test_invalid_sort_option(self):
        with self.assertRaises(ValueError):
            browse_movies(sort_by="invalid")


if __name__ == "__main__":
    unittest.main(verbosity=2)
