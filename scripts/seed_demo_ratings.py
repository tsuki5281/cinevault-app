
"""
Seed clearly labelled demo ratings for CineVault.

These scores are illustrative coursework demo data,
not genuine audience ratings.

Only adds missing ratings. Existing ratings are preserved.
"""

from db.mariadb import get_connection
from db.mongodb import get_review

# DEMO RATING DATA (username, movie_id, stars)
DEMO_RATINGS = [
    # 3 Idiots (s101)
    ("sample_user_11", "s101", 5),
    ("sample_user_03", "s101", 5),
    ("sample_user_06", "s101", 5),
    ("sample_user_09", "s101", 4),

    # #Alive (s28)
    ("sample_user_05", "s28", 4),
    ("sample_user_06", "s28", 4),
    ("sample_user_01", "s28", 5),
    ("sample_user_11", "s28", 4),

    # 365 Days (s107)
    ("sample_user_10", "s107", 1),
    ("sample_user_02", "s107", 2),
    ("sample_user_06", "s107", 2),

    # 50 First Dates (s122)
    ("sample_user_03", "s122", 5),
    ("sample_user_09", "s122", 4),
    ("sample_user_06", "s122", 5),

    # 6 Underground (s128)
    ("sample_user_09", "s128", 3),
    ("sample_user_10", "s128", 4),
    ("sample_user_03", "s128", 4),

    # 1920 (s10)
    ("sample_user_10", "s10", 3),
    ("sample_user_03", "s10", 4),
]


# SEED DEMO RATINGS
def seed_demo_ratings():

    connection = get_connection()

    inserted = 0
    unchanged = 0

    try:

        # Retrieve actual user IDs and validate movie IDs
        usernames = sorted({item[0] for item in DEMO_RATINGS})
        movie_ids = sorted({item[1] for item in DEMO_RATINGS})

        with connection.cursor() as cursor:

            user_placeholders = ", ".join(["%s"] * len(usernames))
            cursor.execute(
                f"""
                SELECT user_id, username
                FROM users
                WHERE username IN ({user_placeholders})
                """,
                usernames
            )

            user_ids = {
                row["username"]: row["user_id"]
                for row in cursor.fetchall()
            }

            missing_users = set(usernames) - set(user_ids)

            if missing_users:
                raise ValueError(
                    f"Missing sample users: {sorted(missing_users)}"
                )

            movie_placeholders = ", ".join(["%s"] * len(movie_ids))

            cursor.execute(
                f"""
                SELECT movie_id
                FROM movies
                WHERE movie_id IN ({movie_placeholders})
                """,
                movie_ids
            )

            existing_movies = {
                row["movie_id"]
                for row in cursor.fetchall()
            }

            missing_movies = set(movie_ids) - existing_movies

            if missing_movies:
                raise ValueError(
                    f"Missing movies: {sorted(missing_movies)}"
                )

        # Make sure every rating corresponds to an actual
        # imported sample review by the same user.
        for username, movie_id, stars in DEMO_RATINGS:

            user_id = user_ids[username]

            review = get_review(user_id, movie_id)

            if review is None:
                raise ValueError(
                    f"No matching review found for "
                    f"{username}, movie {movie_id}"
                )

            if type(stars) is not int or not 1 <= stars <= 5:
                raise ValueError(
                    f"Invalid rating for {username}, {movie_id}"
                )

        # Insert ratings without overwriting existing ones.
        with connection.cursor() as cursor:

            for username, movie_id, stars in DEMO_RATINGS:

                user_id = user_ids[username]

                cursor.execute(
                    """
                    INSERT IGNORE INTO ratings
                        (user_id, movie_id, stars)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, movie_id, stars)
                )

                if cursor.rowcount == 1:
                    inserted += 1
                else:
                    unchanged += 1

        connection.commit()

        print("\nDemo rating seed completed!")
        print(f"New ratings inserted: {inserted}")
        print(f"Existing ratings preserved: {unchanged}")
        print(f"Total demo rating assignments: {len(DEMO_RATINGS)}")

    except Exception:
        connection.rollback()
        print("Demo rating seed failed. Changes rolled back.")
        raise

    finally:
        connection.close()


# MAIN
if __name__ == "__main__":
    seed_demo_ratings()
