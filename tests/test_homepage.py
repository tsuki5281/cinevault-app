
import unittest

from db.home import get_homepage_data


class TestHomepage(unittest.TestCase):

    def test_homepage_returns_all_sections(self):
        results = get_homepage_data()

        self.assertIn("featured_movie", results)
        self.assertIn("highest_rated", results)
        self.assertIn("most_reviewed", results)
        self.assertIn("genres", results)

        self.assertIsInstance(results["highest_rated"], list)
        self.assertIsInstance(results["most_reviewed"], list)
        self.assertIsInstance(results["genres"], list)

    def test_featured_movie_matches_highest_rated(self):
        results = get_homepage_data()

        if results["highest_rated"]:
            featured = results["featured_movie"]
            top_movie = results["highest_rated"][0]

            self.assertIsNotNone(featured)
            self.assertEqual(
                featured["movie_id"],
                top_movie["movie_id"]
            )
            self.assertEqual(
                featured["average_rating"],
                top_movie["average_rating"]
            )
            self.assertEqual(
                featured["rating_count"],
                top_movie["rating_count"]
            )
        else:
            self.assertIsNone(results["featured_movie"])

    def test_homepage_limits(self):
        results = get_homepage_data(
            highest_rated_limit=3,
            most_reviewed_limit=4
        )

        self.assertLessEqual(len(results["highest_rated"]), 3)
        self.assertLessEqual(len(results["most_reviewed"]), 4)

    def test_invalid_limits(self):
        invalid_values = [0, -1, True, "5"]

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    get_homepage_data(highest_rated_limit=value)

                with self.assertRaises(ValueError):
                    get_homepage_data(most_reviewed_limit=value)


if __name__ == "__main__":
    unittest.main()
