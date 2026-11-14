
"""
CineVault authentication module.

Handles:
- Official account registration
- Password verification using Argon2id
- Demo user retrieval
- User account retrieval
"""

import pymysql

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError

from db.mariadb import get_connection

# PASSWORD HASHING CONFIGURATION
password_hasher = PasswordHasher(type=Type.ID)

# GET DEMO USERS
def get_demo_users():
    """
    Retrieve the available sample users.

    Returns:
        A list of dictionaries containing user_id and username.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT user_id, username
                FROM users
                ORDER BY username
            """)

            results = cursor.fetchall()

        # Keep only CineVault's sample demo accounts.
        return [
            user for user in results
            if user["username"].startswith("sample_user_")
        ]

    finally:
        connection.close()

# CREATE OFFICIAL USER ACCOUNT
def create_user(username, password):
    """
    Create a user and store their Argon2id password hash.

    Returns:
        Dictionary containing user_id and username.

    Raises:
        ValueError if the input is invalid or username exists.
    """

    username = username.strip()

    if not 3 <= len(username) <= 50:
        raise ValueError(
            "Username must contain between 3 and 50 characters."
        )

    if username.startswith("sample_user_"):
        raise ValueError(
            "This username prefix is reserved for demo accounts."
        )

    if not isinstance(password, str) or not 8 <= len(password) <= 128:
        raise ValueError(
            "Password must contain between 8 and 128 characters."
        )

    # Hash the password before storing it.
    password_hash = password_hasher.hash(password)

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            # Create the user in the existing users table.
            cursor.execute(
                """
                INSERT INTO users (username)
                VALUES (%s)
                """,
                (username,)
            )

            user_id = cursor.lastrowid

            # Store the password hash separately.
            cursor.execute(
                """
                INSERT INTO user_credentials
                    (user_id, password_hash)
                VALUES (%s, %s)
                """,
                (user_id, password_hash)
            )

        connection.commit()

        return {
            "user_id": user_id,
            "username": username,
            "account_type": "official"
        }

    except pymysql.err.IntegrityError as error:

        connection.rollback()

        if error.args[0] == 1062:
            raise ValueError(
                "This username is already registered."
            ) from error

        raise

    except Exception:

        connection.rollback()
        raise

    finally:
        connection.close()

# AUTHENTICATE OFFICIAL USER
def authenticate_user(username, password):
    """
    Verify an official user's username and password.

    Returns:
        User dictionary if authentication succeeds.
        None if credentials are incorrect.
    """

    username = username.strip()

    if not username or not password:
        return None

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    u.user_id,
                    u.username,
                    c.password_hash
                FROM users u
                JOIN user_credentials c
                    ON u.user_id = c.user_id
                WHERE u.username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

        if user is None:
            return None

        try:

            password_hasher.verify(
                user["password_hash"],
                password
            )

        except VerificationError:
            return None

        # Never return the password hash to the application.
        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "account_type": "official"
        }

    finally:
        connection.close()

# GET USER BY ID
def get_user_by_id(user_id):
    """
    Retrieve a user using their unique user ID.

    Returns:
        User dictionary or None.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT user_id, username
                FROM users
                WHERE user_id = %s
                """,
                (user_id,)
            )

            return cursor.fetchone()

    finally:
        connection.close()
