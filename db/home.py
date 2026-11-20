
from db.catalogue import get_all_genres, get_movie_details
from db.mariadb import get_highest_rated_movies
from db.mongodb import get_most_reviewed_movies


# Retrieves all data required by the Home page.
def get_homepage_data(highest_rated_limit=10, most_reviewed_limit=10):
    if type(highest_rated_limit) is not int or highest_rated_limit < 1:
        raise ValueError("Highest-rated limit must be a positive integer.")

    if type(most_reviewed_limit) is not int or most_reviewed_limit < 1:
        raise ValueError("Most-reviewed limit must be a positive integer.")

    highest_rated = get_highest_rated_movies(
        minimum_ratings=2,
        limit=highest_rated_limit
    )

    most_reviewed = get_most_reviewed_movies(
        limit=most_reviewed_limit
    )

    genres = get_all_genres()

    featured_movie = None

    if highest_rated:
        top_movie = highest_rated[0]

        featured_movie = get_movie_details(
            top_movie["movie_id"]
        )

        if featured_movie is not None:
            featured_movie["average_rating"] = (
                top_movie["average_rating"]
            )
            featured_movie["rating_count"] = (
                top_movie["rating_count"]
            )

    return {
        "featured_movie": featured_movie,
        "highest_rated": highest_rated,
        "most_reviewed": most_reviewed,
        "genres": genres
    }
