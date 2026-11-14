
import unittest

from db.catalogue import get_recommended_actors


class TestRecommendedActors(unittest.TestCase):

    def test_returns_twelve_recommended_actors(self):
        results = get_recommended_actors()

        self.assertEqual(len(results), 12)

    def test_actor_records_have_required_fields(self):
        results = get_recommended_actors()

        for actor in results:
            self.assertIn("actor_id", actor)
            self.assertIn("actor_name", actor)
            self.assertIn("movie_count", actor)
            self.assertIn("movie_id", actor)
            self.assertIn("title", actor)

            self.assertGreater(actor["movie_count"], 0)

    def test_recommended_actors_are_unique(self):
        results = get_recommended_actors()

        actor_ids = [
            actor["actor_id"]
            for actor in results
        ]

        self.assertEqual(
            len(actor_ids),
            len(set(actor_ids))
        )

    def test_actors_are_ranked_by_movie_count(self):
        results = get_recommended_actors()

        movie_counts = [
            actor["movie_count"]
            for actor in results
        ]

        self.assertEqual(
            movie_counts,
            sorted(movie_counts, reverse=True)
        )

    
    def test_recommendations_use_demo_movies(self):
        results = get_recommended_actors()

        demo_movie_ids = {
            "s101", "s28", "s107",
            "s122", "s128", "s10"
        }

        self.assertEqual(len(results), 12)

        for actor in results:
            self.assertIn(
                actor["movie_id"],
                demo_movie_ids
            )

    def test_featured_movies_are_associated_with_actors(self):
        results = get_recommended_actors()

        connection_pairs = [
            (actor["actor_id"], actor["movie_id"])
            for actor in results
        ]

        self.assertEqual(len(connection_pairs), 12)

        # Verify each recommended actor is actually credited.
        from db.mariadb import get_connection

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for actor_id, movie_id in connection_pairs:
                    cursor.execute(
                        """
                        SELECT COUNT(*) AS credit_count
                        FROM movie_actors
                        WHERE actor_id = %s AND movie_id = %s
                        """,
                        (actor_id, movie_id)
                    )

                    result = cursor.fetchone()

                    self.assertEqual(
                        result["credit_count"],
                        1
                    )

        finally:
            connection.close()

    def test_custom_limit(self):
        results = get_recommended_actors(limit=8)

        self.assertEqual(len(results), 8)

    def test_invalid_limit(self):
        for limit in [0, -1, 25, True]:
            with self.subTest(limit=limit):
                with self.assertRaises(ValueError):
                    get_recommended_actors(limit=limit)


if __name__ == "__main__":
    unittest.main()
