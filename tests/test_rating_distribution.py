
import unittest
import uuid

from db.mariadb import (
    get_connection,
    add_rating,
    update_rating,
    delete_rating,
    get_rating_distribution,
)


class TestRatingDistribution(unittest.TestCase):

    def setUp(self):
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
        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for user_id in self.user_ids:
                    cursor.execute(
                        "DELETE FROM ratings WHERE user_id = %s",
                        (user_id,)
                    )
                    cursor.execute(
                        "DELETE FROM users WHERE user_id = %s",
                        (user_id,)
                    )

            connection.commit()

        finally:
            connection.close()

    def test_rating_distribution(self):
        initial = get_rating_distribution(self.movie_id)

        self.assertEqual(list(initial.keys()), [1, 2, 3, 4, 5])

        expected = initial.copy()

        add_rating(self.user1, self.movie_id, 1)
        add_rating(self.user2, self.movie_id, 5)

        expected[1] += 1
        expected[5] += 1

        self.assertEqual(
            get_rating_distribution(self.movie_id),
            expected
        )

        update_rating(self.user1, self.movie_id, 3)

        expected[1] -= 1
        expected[3] += 1

        self.assertEqual(
            get_rating_distribution(self.movie_id),
            expected
        )

        delete_rating(self.user2, self.movie_id)

        expected[5] -= 1

        self.assertEqual(
            get_rating_distribution(self.movie_id),
            expected
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
