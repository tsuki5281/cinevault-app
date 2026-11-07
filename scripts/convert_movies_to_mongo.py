# Conversion script: MariaDB movie catalogue -> MongoDB documents
#
# The relational design spreads one movie across 5 tables:
#   movies, genres, movie_genres, actors, movie_actors
# MongoDB stores the same movie as ONE document, with genres and actors
# embedded as arrays, e.g.
#   {"movie_id": "s10", "title": "...", "director": "...", "country": "...",
#    "description": "...", "genres": ["Dramas", ...], "actors": ["...", ...]}
#
# Run from the repository root (after scripts.import_movies):
#   python -m scripts.convert_movies_to_mongo

from pymongo import ASCENDING

from db.mariadb import get_connection
from db.mongodb import get_mongo_db


# Reads every movie, plus its genres and actors, from MariaDB
def read_movies_from_mariadb():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT movie_id, title, director, country, description
                FROM movies
                ORDER BY movie_id
            """)
            movie_rows = cursor.fetchall()

            cursor.execute("""
                SELECT mg.movie_id, g.genre_name
                FROM movie_genres AS mg
                JOIN genres AS g ON mg.genre_id = g.genre_id
                ORDER BY mg.movie_id, g.genre_name
            """)
            genre_rows = cursor.fetchall()

            cursor.execute("""
                SELECT ma.movie_id, a.actor_name
                FROM movie_actors AS ma
                JOIN actors AS a ON ma.actor_id = a.actor_id
                ORDER BY ma.movie_id, a.actor_name
            """)
            actor_rows = cursor.fetchall()

    finally:
        connection.close()

    return movie_rows, genre_rows, actor_rows


# Converts the relational rows into one document per movie
def build_movie_documents(movie_rows, genre_rows, actor_rows):
    documents = {}

    for row in movie_rows:
        documents[row["movie_id"]] = {
            "movie_id": row["movie_id"],
            "title": row["title"],
            "director": row["director"],
            "country": row["country"],
            "description": row["description"],
            "genres": [],
            "actors": [],
        }

    # Embed genres (replaces the movie_genres + genres join)
    for row in genre_rows:
        if row["movie_id"] in documents:
            documents[row["movie_id"]]["genres"].append(row["genre_name"])

    # Embed actors (replaces the movie_actors + actors join)
    for row in actor_rows:
        if row["movie_id"] in documents:
            documents[row["movie_id"]]["actors"].append(row["actor_name"])

    result = []
    for movie_id in documents:
        result.append(documents[movie_id])
    return result


def main():
    movie_rows, genre_rows, actor_rows = read_movies_from_mariadb()
    print(f"Read from MariaDB: {len(movie_rows)} movies, "
          f"{len(genre_rows)} movie-genre links, {len(actor_rows)} movie-actor links")

    documents = build_movie_documents(movie_rows, genre_rows, actor_rows)

    movies = get_mongo_db()["movies"]
    movies.delete_many({})
    if len(documents) > 0:
        movies.insert_many(documents)

    # Indexes: unique movie_id, plus multikey indexes on the embedded arrays
    movies.create_index([("movie_id", ASCENDING)], unique=True, name="uniq_movie_id")
    movies.create_index([("genres", ASCENDING)], name="genres")
    movies.create_index([("actors", ASCENDING)], name="actors")

    # Check that nothing was lost in the conversion
    mongo_count = movies.count_documents({})
    print(f"Written to MongoDB 'movies' collection: {mongo_count} documents")
    if mongo_count != len(movie_rows):
        raise RuntimeError("Movie counts do not match between MariaDB and MongoDB.")

    print("Example document:")
    print(movies.find_one({"movie_id": documents[0]["movie_id"]}, {"_id": 0}))
    print("Conversion completed successfully!")


if __name__ == "__main__":
    main()
