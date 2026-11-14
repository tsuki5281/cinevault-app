
import unittest
import uuid

from db.authentication import (
    create_user,
    authenticate_user,
    get_demo_users
)
from db.mariadb import get_connection


class TestAuthentication(unittest.TestCase):

    def setUp(self):
        self.username = "test_auth_" + uuid.uuid4().hex[:10]
        self.password = "ValidPass123!"
        self.created_user_ids = []

    def tearDown(self):
        if not self.created_user_ids:
            return

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                for user_id in self.created_user_ids:
                    cursor.execute(
                        "DELETE FROM user_credentials WHERE user_id = %s",
                        (user_id,)
                    )

                    cursor.execute(
                        "DELETE FROM users WHERE user_id = %s",
                        (user_id,)
                    )

            connection.commit()

        finally:
            connection.close()

    def register_test_user(self):
        user = create_user(self.username, self.password)
        self.created_user_ids.append(user["user_id"])
        return user

    def test_create_user(self):
        user = self.register_test_user()

        self.assertEqual(user["username"], self.username)
        self.assertEqual(user["account_type"], "official")
        self.assertIn("user_id", user)

    def test_successful_login(self):
        user = self.register_test_user()

        result = authenticate_user(
            self.username,
            self.password
        )

        self.assertEqual(result["user_id"], user["user_id"])
        self.assertEqual(result["username"], self.username)

    def test_incorrect_password(self):
        self.register_test_user()

        result = authenticate_user(
            self.username,
            "WrongPassword123!"
        )

        self.assertIsNone(result)

    def test_nonexistent_user(self):
        result = authenticate_user(
            self.username,
            self.password
        )

        self.assertIsNone(result)

    def test_empty_credentials(self):
        self.assertIsNone(
            authenticate_user("", self.password)
        )

        self.assertIsNone(
            authenticate_user(self.username, "")
        )

    def test_duplicate_username(self):
        self.register_test_user()

        with self.assertRaises(ValueError):
            create_user(self.username, self.password)

    def test_invalid_registration_inputs(self):
        invalid_inputs = [
            ("ab", self.password),
            ("sample_user_fake", self.password),
            (self.username, "short"),
            (self.username, "x" * 129)
        ]

        for username, password in invalid_inputs:
            with self.subTest(username=username):
                with self.assertRaises(ValueError):
                    create_user(username, password)

    def test_password_is_stored_as_hash(self):
        user = self.register_test_user()

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT password_hash
                    FROM user_credentials
                    WHERE user_id = %s
                    """,
                    (user["user_id"],)
                )

                result = cursor.fetchone()

        finally:
            connection.close()

        self.assertIsNotNone(result)
        self.assertNotEqual(
            result["password_hash"],
            self.password
        )
        self.assertTrue(
            result["password_hash"].startswith("$argon2id$")
        )

    def test_demo_users_are_sample_accounts(self):
        users = get_demo_users()

        self.assertGreater(len(users), 0)

        for user in users:
            self.assertTrue(
                user["username"].startswith("sample_user_")
            )


if __name__ == "__main__":
    unittest.main()
