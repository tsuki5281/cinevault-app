import unittest

from db.catalogue import get_movie_card_details


class TestMovieCardDetails(unittest.TestCase):

    def test_returns_movie_dataset_information_only(self):
        results = get_movie_card_details(["s101", "s28"])

        self.assertEqual(len(results), 2)

        for movie_id, movie in results.items():
            self.assertEqual(movie["movie_id"], movie_id)
            self.assertIn("title", movie)
            self.assertIn("genres", movie)
            self.assertNotIn("average_rating", movie)
            self.assertNotIn("rating_count", movie)

    def test_genres_are_returned(self):
        results = get_movie_card_details(["s101"])

        self.assertNotEqual(results["s101"]["genres"], "")

    def test_duplicate_ids_are_removed(self):
        results = get_movie_card_details(
            ["s101", "s101", "s28"]
        )

        self.assertEqual(len(results), 2)

    def test_unknown_movie_is_omitted(self):
        results = get_movie_card_details(
            ["s101", "s99999999"]
        )

        self.assertIn("s101", results)
        self.assertNotIn("s99999999", results)

    def test_empty_list(self):
        self.assertEqual(get_movie_card_details([]), {})

    def test_invalid_input(self):
        invalid_inputs = [
            "s101",
            ["", "s101"],
            [None],
            [123]
        ]

        for movie_ids in invalid_inputs:
            with self.subTest(movie_ids=movie_ids):
                with self.assertRaises(ValueError):
                    get_movie_card_details(movie_ids)

    def test_too_many_movie_ids(self):
        movie_ids = [f"s{i}" for i in range(101)]

        with self.assertRaises(ValueError):
            get_movie_card_details(movie_ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
