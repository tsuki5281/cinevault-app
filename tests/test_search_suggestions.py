
import unittest
import uuid

from db.mariadb import get_connection
from db.catalogue import get_search_suggestions


class TestSearchSuggestions(unittest.TestCase):

    def setUp(self):
        self.keyword = "CVSEARCH" + uuid.uuid4().hex[:8]
        self.movie_ids = []

        self.actor_name = self.keyword + " Test Actor"
        self.genre_name = self.keyword + " Test Genre"

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                movie_titles = [
                    self.keyword + " Test Movie",
                    "Extra " + self.keyword + " Test Movie"
                ]

                for title in movie_titles:
                    movie_id = "s" + uuid.uuid4().hex[:8]

                    cursor.execute(
                        """
                        INSERT INTO movies
                            (movie_id, title, director, country, description)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            movie_id,
                            title,
                            "Test Director",
                            "Singapore",
                            "Temporary test movie"
                        )
                    )

                    self.movie_ids.append(movie_id)

                cursor.execute(
                    "INSERT INTO actors (actor_name) VALUES (%s)",
                    (self.actor_name,)
                )

                cursor.execute(
                    "INSERT INTO genres (genre_name) VALUES (%s)",
                    (self.genre_name,)
                )

            connection.commit()

        finally:
            connection.close()

    def tearDown(self):
        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for movie_id in self.movie_ids:
                    cursor.execute(
                        "DELETE FROM movies WHERE movie_id = %s",
                        (movie_id,)
                    )

                cursor.execute(
                    "DELETE FROM actors WHERE actor_name = %s",
                    (self.actor_name,)
                )

                cursor.execute(
                    "DELETE FROM genres WHERE genre_name = %s",
                    (self.genre_name,)
                )

            connection.commit()

        finally:
            connection.close()

    def test_suggestions_return_all_three_categories(self):
        results = get_search_suggestions(self.keyword)

        self.assertEqual(len(results["movies"]), 2)
        self.assertEqual(len(results["actors"]), 1)
        self.assertEqual(len(results["genres"]), 1)

        self.assertEqual(
            results["actors"][0]["actor_name"],
            self.actor_name
        )

        self.assertEqual(
            results["genres"][0]["genre_name"],
            self.genre_name
        )

    def test_prefix_matches_appear_first(self):
        results = get_search_suggestions(self.keyword)

        self.assertEqual(
            results["movies"][0]["title"],
            self.keyword + " Test Movie"
        )

    def test_result_limit(self):
        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for i in range(3):
                    movie_id = "s" + uuid.uuid4().hex[:8]

                    cursor.execute(
                        """
                        INSERT INTO movies
                            (movie_id, title, director, country, description)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            movie_id,
                            self.keyword + " Extra Movie " + str(i),
                            "Test Director",
                            "Singapore",
                            "Temporary test movie"
                        )
                    )

                    self.movie_ids.append(movie_id)

            connection.commit()

        finally:
            connection.close()

        results = get_search_suggestions(self.keyword, limit=2)

        self.assertEqual(len(results["movies"]), 2)

    def test_empty_keyword(self):
        with self.assertRaises(ValueError):
            get_search_suggestions("   ")

    def test_invalid_limit(self):
        for limit in [0, 21, True]:
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    get_search_suggestions(self.keyword, limit=limit)

    def test_unmatched_keyword(self):
        results = get_search_suggestions(
            "NO_MATCH_" + uuid.uuid4().hex
        )

        self.assertEqual(results["movies"], [])
        self.assertEqual(results["actors"], [])
        self.assertEqual(results["genres"], [])


if __name__ == "__main__":
    unittest.main()
