
from datetime import datetime, timezone

from db.mariadb import get_connection, get_user_ratings
from db.mongodb import get_user_reviews, get_reviews_collection


def _datetime_sort_key(value):
    if value is None:
        return datetime.min

    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    return value


# Combines a user's ratings and reviews into one entry per movie.
def get_user_contributions(user_id):
    if type(user_id) is not int or user_id < 1:
        raise ValueError("User ID must be a positive integer.")

    ratings = get_user_ratings(user_id)

    reviews = []
    offset = 0
    page_size = 20

    while True:
        batch = get_user_reviews(
            user_id,
            limit=page_size,
            offset=offset
        )

        reviews.extend(batch)

        if len(batch) < page_size:
            break

        offset += page_size

    contributions = {}

    for rating in ratings:
        movie_id = rating["movie_id"]

        contributions[movie_id] = {
            "movie_id": movie_id,
            "title": rating["title"],
            "rating_stars": rating["stars"],
            "rating_updated_at": rating["updated_at"],
            "review_text": None,
            "review_spoiler": None,
            "review_tags": [],
            "review_created_at": None
        }

    missing_movie_ids = [
        review["movie_id"]
        for review in reviews
        if review["movie_id"] not in contributions
    ]

    titles = {}

    if missing_movie_ids:
        placeholders = ", ".join(["%s"] * len(missing_movie_ids))

        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                sql = f"""
                    SELECT movie_id, title
                    FROM movies
                    WHERE movie_id IN ({placeholders})
                """

                cursor.execute(sql, missing_movie_ids)

                titles = {
                    row["movie_id"]: row["title"]
                    for row in cursor.fetchall()
                }

        finally:
            connection.close()

    for review in reviews:
        movie_id = review["movie_id"]

        if movie_id not in contributions:
            contributions[movie_id] = {
                "movie_id": movie_id,
                "title": titles.get(movie_id),
                "rating_stars": None,
                "rating_updated_at": None,
                "review_text": None,
                "review_spoiler": None,
                "review_tags": [],
                "review_created_at": None
            }

        contributions[movie_id].update({
            "review_text": review["review_text"],
            "review_spoiler": review["spoiler"],
            "review_tags": review.get("tags", []),
            "review_created_at": review["created_at"]
        })

    result = list(contributions.values())

    for entry in result:
        activity_dates = [
            date
            for date in (
                entry["rating_updated_at"],
                entry["review_created_at"]
            )
            if date is not None
        ]

        entry["last_activity_at"] = (
            max(activity_dates, key=_datetime_sort_key)
            if activity_dates
            else None
        )

    result.sort(
        key=lambda entry: _datetime_sort_key(
            entry["last_activity_at"]
        ),
        reverse=True
    )

    return result

from db.mongodb import get_reviews_collection


# Retrieves activity counts for a user's profile summary.
def get_user_activity_summary(user_id):
    if type(user_id) is not int or user_id < 1:
        raise ValueError("User ID must be a positive integer.")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    (SELECT COUNT(*)
                     FROM ratings
                     WHERE user_id = %s) AS movies_rated,

                    (SELECT COUNT(*)
                     FROM watched_movies
                     WHERE user_id = %s) AS movies_watched,

                    (SELECT COUNT(*)
                     FROM watchlist
                     WHERE user_id = %s) AS watchlist_items
                """,
                (user_id, user_id, user_id)
            )

            summary = cursor.fetchone()

    finally:
        connection.close()

    summary["reviews_written"] = (
        get_reviews_collection().count_documents(
            {"user_id": user_id}
        )
    )

    return summary
