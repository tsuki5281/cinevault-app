# MariaDB functions
import os

import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
    )


# Ratings CRUD operations

# Adds a new rating for a movie by a user
# Rating must be between 1 and 5 stars
def add_rating(user_id, movie_id, stars):
    if not isinstance(stars, int) or not 1 <= stars <= 5:
        raise ValueError("Rating must be an integer between 1 and 5.")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO ratings (user_id, movie_id, stars)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (user_id, movie_id, stars))

        connection.commit()
        return True

    except pymysql.err.IntegrityError as error:
        connection.rollback()

        # Error 1062: Duplicate entry (user has already rated this movie)
        if error.args[0] == 1062:
            return False

        # Error 1452: Foreign key constraint fails (invalid user_id or movie_id)
        elif error.args[0] == 1452:
            raise ValueError("Invalid user ID or movie ID.") from error

        raise

    finally:
        connection.close()

# Retrieves a user's rating for a specific movie.
# Returns the rating details or None if no rating exists.
def get_rating(user_id, movie_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT stars, updated_at
                FROM ratings
                WHERE user_id = %s AND movie_id = %s
            """
            cursor.execute(sql, (user_id, movie_id))
            result = cursor.fetchone()

        return result

    finally:
        connection.close()

# Updates an existing rating for a specific movie.
# Rating must be between 1 and 5 stars.
def update_rating(user_id, movie_id, stars):
    if not isinstance(stars, int) or not 1 <= stars <= 5:
        raise ValueError("Rating must be an integer between 1 and 5.")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE ratings
                SET stars = %s
                WHERE user_id = %s AND movie_id = %s
            """
            cursor.execute(sql, (stars, user_id, movie_id))

        connection.commit()
        return cursor.rowcount > 0

    finally:
        connection.close()

# Deletes a user's rating for a specific movie.
# Returns True if a rating was deleted, else False
def delete_rating(user_id, movie_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                DELETE FROM ratings
                WHERE user_id = %s AND movie_id = %s
            """
            cursor.execute(sql, (user_id, movie_id))

        connection.commit()
        return cursor.rowcount > 0

    finally:
        connection.close()
# ------------------------------------------------------------------------------------------------------
# Average Rating & Advanced SQL

# Calculates the average rating for a specific movie.
# Returns None if the movie has no ratings.
def get_average_rating(movie_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT AVG(stars) AS average_rating
                FROM ratings
                WHERE movie_id = %s
            """
            cursor.execute(sql, (movie_id,))
            result = cursor.fetchone()

        return result["average_rating"]

    finally:
        connection.close()

# Counts the number of ratings for a specific movie.
# Returns the total number of ratings.
def get_rating_count(movie_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT COUNT(*) AS rating_count
                FROM ratings
                WHERE movie_id = %s
            """
            cursor.execute(sql, (movie_id,))
            result = cursor.fetchone()

        return result["rating_count"]

    finally:
        connection.close()

# Retrieves the highest rated movies based on average user ratings.
# For testing purposes, the minimum is set to 2 ratings.
# This threshold can be increased depending on the number of ratings
# available in the database.
# Uses JOIN, AVG(), COUNT(), GROUP BY and HAVING.
def get_highest_rated_movies(minimum_ratings=2, limit=10):

    # Validates that both parameters are positive integers.
    if type(minimum_ratings) is not int or minimum_ratings < 1:
        raise ValueError("Minimum ratings must be a positive integer.")

    if type(limit) is not int or limit < 1:
        raise ValueError("Limit must be a positive integer.")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    m.movie_id,
                    m.title,
                    AVG(r.stars) AS average_rating,
                    COUNT(r.user_id) AS rating_count
                FROM movies AS m
                JOIN ratings AS r
                    ON m.movie_id = r.movie_id
                GROUP BY m.movie_id, m.title
                HAVING COUNT(r.user_id) >= %s
                ORDER BY average_rating DESC, rating_count DESC
                LIMIT %s
            """
            cursor.execute(sql, (minimum_ratings, limit))
            result = cursor.fetchall()

        return result

    finally:
        connection.close()
# ------------------------------------------------------------------------------------------------------
# Watchlist CRUD operations

# Adds a movie to a specific user's watchlist.
# Returns True if successful, otherwise False.
def add_to_watchlist(user_id, movie_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO watchlist (user_id, movie_id)
                VALUES (%s, %s)
            """
            cursor.execute(sql, (user_id, movie_id))

        connection.commit()
        return True

    except pymysql.err.IntegrityError as error:
        connection.rollback()

        # Error 1062: Duplicate entry (user has already added this movie to their watchlist)
        if error.args[0] == 1062:
            return False

        # Error 1452: Foreign key constraint fails (invalid user_id or movie_id)
        elif error.args[0] == 1452:
            raise ValueError("Invalid user ID or movie ID.") from error
        
        raise

    finally:
        connection.close()


# Retrieves all movies in a specific user's watchlist.
# Returns movie details, including the date each movie was added.
def get_watchlist(user_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    m.movie_id,
                    m.title,
                    w.added_at
                FROM watchlist AS w
                JOIN movies AS m
                    ON w.movie_id = m.movie_id
                WHERE w.user_id = %s
                ORDER BY w.added_at DESC
            """
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()

        return result

    finally:
        connection.close()


# Removes a movie from a specific user's watchlist.
# Returns True if a movie was removed, otherwise False.
def remove_from_watchlist(user_id, movie_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = """
                DELETE FROM watchlist
                WHERE user_id = %s AND movie_id = %s
            """
            cursor.execute(sql, (user_id, movie_id))

        connection.commit()
        return cursor.rowcount > 0

    finally:
        connection.close()

if __name__ == "__main__":
    connection = get_connection()
    print("MariaDB connection successful!")
    connection.close()

