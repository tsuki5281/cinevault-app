
import unittest

from db.catalogue import get_all_genres


class TestGetAllGenres(unittest.TestCase):

    def test_returns_genres(self):
        results = get_all_genres()

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_genre_records_have_required_fields(self):
        results = get_all_genres()

        for genre in results:
            self.assertIn("genre_id", genre)
            self.assertIn("genre_name", genre)
            self.assertIsNotNone(genre["genre_id"])
            self.assertIsNotNone(genre["genre_name"])

    def test_genres_are_alphabetically_sorted(self):
        results = get_all_genres()

        names = [
            genre["genre_name"]
            for genre in results
        ]

        self.assertEqual(
            names,
            sorted(names, key=str.casefold)
        )

    def test_genres_are_unique(self):
        results = get_all_genres()

        genre_ids = [genre["genre_id"] for genre in results]
        genre_names = [genre["genre_name"] for genre in results]

        self.assertEqual(len(genre_ids), len(set(genre_ids)))
        self.assertEqual(len(genre_names), len(set(genre_names)))


if __name__ == "__main__":
    unittest.main()
