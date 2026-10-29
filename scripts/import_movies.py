# Data cleaning and import scripts 
import pandas as pd
import pymysql
from pathlib import Path
import os
from dotenv import load_dotenv
import unicodedata

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Cleaned Netflix movie dataset
CSV_PATH = BASE_DIR / "data" / "netflix_movies_cleaned.csv"

# Load the cleaned movie dataset
df = pd.read_csv(CSV_PATH)

# Verify the dataset structure
expected_cols = [
    "movie_id",
    "title",
    "genre",
    "director",
    "cast",
    "country",
    "description"
]

if list(df.columns) != expected_cols:
    raise ValueError("Dataset columns do not match the expected structure.")

print(f"Dataset loaded successfully: {len(df)} movies")

# Load database credentials
load_dotenv(BASE_DIR / ".env")


# Import movie information into MariaDB
def import_movies(df, connection):
    sql = """
        INSERT INTO movies
            (movie_id, title, director, country, description)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE movie_id = movie_id
    """

    movie_records = list(
        df[["movie_id", "title", "director", "country", "description"]]
        .itertuples(index=False, name=None)
    )

    with connection.cursor() as cursor:
        cursor.executemany(sql, movie_records)

# Import unique movie genres into MariaDB
def import_genres(df, connection):

    # Extract and split genre names
    genres = set()

    for genre_list in df["genre"]:
        for genre in genre_list.split(","):
            genre = genre.strip()

            if genre:
                genres.add(genre)

    # Insert unique genres
    sql = """
        INSERT INTO genres (genre_name)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE genre_name = genre_name
    """

    genre_records = [(genre,) for genre in sorted(genres)]

    with connection.cursor() as cursor:
        cursor.executemany(sql, genre_records)

# Import unique movie actors into MariaDB
def import_actors(df, connection):

    # Extract and split actor names
    actors = set()

    for cast_list in df["cast"]:
        for actor in cast_list.split(","):
            actor = actor.strip()

            if actor:
                actors.add(actor)

    # Insert unique actors
    sql = """
        INSERT INTO actors (actor_name)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE actor_name = actor_name
    """

    actor_records = [(actor,) for actor in sorted(actors)]

    with connection.cursor() as cursor:
        cursor.executemany(sql, actor_records)

# Link each movie to its genres
def import_movie_genres(df, connection):

    with connection.cursor() as cursor:

        # Retrieve genre IDs from MariaDB
        cursor.execute("SELECT genre_id, genre_name FROM genres")
        genre_map = {
            genre_name: genre_id
            for genre_id, genre_name in cursor.fetchall()
        }

        # Prepare movie-genre relationships
        movie_genre_records = []

        for row in df.itertuples(index=False):
            for genre in row.genre.split(","):
                genre = genre.strip()

                if genre:
                    movie_genre_records.append(
                        (row.movie_id, genre_map[genre])
                    )

        # Insert movie-genre relationships
        sql = """
            INSERT INTO movie_genres (movie_id, genre_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE movie_id = movie_id
        """

        cursor.executemany(sql, sorted(set(movie_genre_records)))

# Link each movie to its actors
def import_movie_actors(df, connection):

    with connection.cursor() as cursor:

        # Retrieve actor IDs from MariaDB
        cursor.execute("SELECT actor_id, actor_name FROM actors")

        # Normalise actor names for consistent matching
        def normalise_name(name):
            name = unicodedata.normalize("NFKD", name)
            name = "".join(
                char for char in name
                if not unicodedata.combining(char)
            )
            return name.casefold()

        # Fetch stored actor IDs and names
        actor_rows = cursor.fetchall()
        actor_map = {
            normalise_name(actor_name): actor_id
            for actor_id, actor_name in actor_rows
        }

        # Prepare movie-actor relationships
        movie_actor_records = []

        for row in df.itertuples(index=False):
            for actor in row.cast.split(","):
                actor = actor.strip()

                if actor:
                    actor_key = normalise_name(actor)

                    if actor_key in actor_map:
                        actor_id = actor_map[actor_key]
                    else:
                        # Let MariaDB's collation resolve equivalent names
                        cursor.execute(
                            "SELECT actor_id FROM actors WHERE actor_name = %s",
                            (actor,)
                        )
                        result = cursor.fetchone()

                        if result is None:
                            raise ValueError(f"Actor not found in database: {actor}")

                        actor_id = result[0]
                        actor_map[actor_key] = actor_id

                    movie_actor_records.append((row.movie_id, actor_id))

        # Insert movie-actor relationships
        sql = """
            INSERT INTO movie_actors (movie_id, actor_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE movie_id = movie_id
        """

        cursor.executemany(sql, sorted(set(movie_actor_records)))


# Execute the complete movie catalogue import
def main():

    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME"),
        autocommit=False
    )

    try:
        # Import parent tables first
        import_movies(df, connection)
        import_genres(df, connection)
        import_actors(df, connection)

        # Import junction tables afterwards
        import_movie_genres(df, connection)
        import_movie_actors(df, connection)

        # Save all changes if successful
        connection.commit()
        print("Movie catalogue imported successfully!")

    except Exception:
        # Undo changes if any import operation fails
        connection.rollback()
        print("Import failed. Changes rolled back.")
        raise

    finally:
        # Always close the database connection
        connection.close()


if __name__ == "__main__":
    main()