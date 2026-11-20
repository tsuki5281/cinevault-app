from db.mariadb import get_connection


def get_movie_details(movie_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    movie_id,
                    title,
                    director,
                    country,
                    description
                FROM movies
                WHERE movie_id = %s
            """

            cursor.execute(query, (movie_id,))
            movie = cursor.fetchone()

            if movie is None:
                return None

            genre_query = """
                SELECT g.genre_name
                FROM movie_genres mg
                JOIN genres g ON mg.genre_id = g.genre_id
                WHERE mg.movie_id = %s
                ORDER BY g.genre_name
            """

            cursor.execute(genre_query, (movie_id,))
            genres = cursor.fetchall()

            movie["genres"] = [genre["genre_name"] for genre in genres]

            actor_query = """
                SELECT a.actor_name
                FROM movie_actors ma
                JOIN actors a ON ma.actor_id = a.actor_id
                WHERE ma.movie_id = %s
                ORDER BY a.actor_name
            """

            cursor.execute(actor_query, (movie_id,))
            actors = cursor.fetchall()

            movie["actors"] = [actor["actor_name"] for actor in actors]

            return movie

    finally:
        connection.close()


def browse_movies(
    title=None,
    genres=None,
    actors=None,
    genre_match="all",
    actor_match="all",
    sort_by="title_asc",
    limit=50,
    offset=0
):
    if genre_match not in ("all", "any"):
        raise ValueError("genre_match must be 'all' or 'any'")
    genres = list(dict.fromkeys(genres or []))

    if actor_match not in ("all", "any"):
        raise ValueError("actor_match must be 'all' or 'any'")
    actors = list(dict.fromkeys(actors or []))

    if sort_by not in ("title_asc", "title_desc"):
        raise ValueError("sort_by must be 'title_asc' or 'title_desc'")

    if limit is not None and (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 1 <= limit <= 100
    ):
        raise ValueError("limit must be an integer between 1 and 100, or None")

    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    if limit is None and offset != 0:
        raise ValueError("offset must be 0 when limit is None")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT m.movie_id, m.title
                FROM movies m
                WHERE (%s IS NULL OR m.title LIKE CONCAT('%%', %s, '%%'))
            """

            params = [title, title]

            if genres:
                placeholders = ", ".join(["%s"] * len(genres))

                query += f"""
                    AND m.movie_id IN (
                        SELECT mg.movie_id
                        FROM movie_genres mg
                        JOIN genres g ON mg.genre_id = g.genre_id
                        WHERE g.genre_name IN ({placeholders})
                        GROUP BY mg.movie_id
                        HAVING COUNT(DISTINCT g.genre_id) >= %s
                    )
                """

                params.extend(genres)
                params.append(len(genres) if genre_match == "all" else 1)

            if actors:
                placeholders = ", ".join(["%s"] * len(actors))

                query += f"""
                    AND m.movie_id IN (
                        SELECT ma.movie_id
                        FROM movie_actors ma
                        JOIN actors a ON ma.actor_id = a.actor_id
                        WHERE a.actor_name IN ({placeholders})
                        GROUP BY ma.movie_id
                        HAVING COUNT(DISTINCT a.actor_id) >= %s
                    )
                """

                params.extend(actors)
                params.append(len(actors) if actor_match == "all" else 1)

            if sort_by == "title_asc":
                query += " ORDER BY m.title ASC, m.movie_id ASC"
            else:
                query += " ORDER BY m.title DESC, m.movie_id DESC"

            if limit is not None:
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])

            cursor.execute(query, params)
            return list(cursor.fetchall())

    finally:
        connection.close()

# Retrieves matching movie, actor and genre suggestions.
def get_search_suggestions(keyword, limit=5):
    if not isinstance(keyword, str) or keyword.strip() == "":
        raise ValueError("Search keyword cannot be empty.")

    if type(limit) is not int or not 1 <= limit <= 20:
        raise ValueError("Limit must be between 1 and 20.")

    keyword = keyword.strip()
    prefix = keyword + "%"
    partial = "%" + keyword + "%"

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT movie_id, title
                FROM movies
                WHERE title LIKE %s
                ORDER BY
                    CASE WHEN title LIKE %s THEN 0 ELSE 1 END,
                    title ASC
                LIMIT %s
                """,
                (partial, prefix, limit)
            )
            movies = list(cursor.fetchall())

            cursor.execute(
                """
                SELECT actor_id, actor_name
                FROM actors
                WHERE actor_name LIKE %s
                ORDER BY
                    CASE WHEN actor_name LIKE %s THEN 0 ELSE 1 END,
                    actor_name ASC
                LIMIT %s
                """,
                (partial, prefix, limit)
            )
            actors = list(cursor.fetchall())

            cursor.execute(
                """
                SELECT genre_id, genre_name
                FROM genres
                WHERE genre_name LIKE %s
                ORDER BY
                    CASE WHEN genre_name LIKE %s THEN 0 ELSE 1 END,
                    genre_name ASC
                LIMIT %s
                """,
                (partial, prefix, limit)
            )
            genres = list(cursor.fetchall())

        return {
            "movies": movies,
            "actors": actors,
            "genres": genres
        }

    finally:
        connection.close()



# Retrieves actor recommendations from the curated demo movie collection.
def get_recommended_actors(limit=12):
    if type(limit) is not int or not 1 <= limit <= 24:
        raise ValueError("Limit must be between 1 and 24.")

    demo_movie_ids = (
        "s101",
        "s28",
        "s107",
        "s122",
        "s128",
        "s10"
    )

    placeholders = ", ".join(["%s"] * len(demo_movie_ids))

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = f"""
                WITH demo_movie_cast AS (
                    SELECT
                        a.actor_id,
                        a.actor_name,
                        m.movie_id,
                        m.title
                    FROM movie_actors AS ma
                    JOIN actors AS a
                        ON ma.actor_id = a.actor_id
                    JOIN movies AS m
                        ON ma.movie_id = m.movie_id
                    WHERE m.movie_id IN ({placeholders})
                ),
                actor_counts AS (
                    SELECT
                        actor_id,
                        COUNT(DISTINCT movie_id) AS movie_count
                    FROM movie_actors
                    GROUP BY actor_id
                ),
                ranked_movies AS (
                    SELECT
                        d.actor_id,
                        d.actor_name,
                        d.movie_id,
                        d.title,
                        ac.movie_count,
                        ROW_NUMBER() OVER (
                            PARTITION BY d.actor_id
                            ORDER BY d.title, d.movie_id
                        ) AS movie_rank
                    FROM demo_movie_cast AS d
                    JOIN actor_counts AS ac
                        ON d.actor_id = ac.actor_id
                )
                SELECT
                    actor_id,
                    actor_name,
                    movie_count,
                    movie_id,
                    title
                FROM ranked_movies
                WHERE movie_rank = 1
                ORDER BY movie_count DESC, actor_name ASC
                LIMIT %s
            """

            cursor.execute(sql, list(demo_movie_ids) + [limit])
            return list(cursor.fetchall())

    finally:
        connection.close()



# Retrieves all available genres for catalogue exploration.
def get_all_genres():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    genre_id,
                    genre_name
                FROM genres
                ORDER BY genre_name ASC
                """
            )

            return list(cursor.fetchall())

    finally:
        connection.close()

# Retrieves movie title and genre information for multiple movie cards.
def get_movie_card_details(movie_ids):
    if not isinstance(movie_ids, (list, tuple)):
        raise ValueError("Movie IDs must be a list or tuple.")

    if len(movie_ids) > 100:
        raise ValueError("A maximum of 100 movie IDs is allowed.")

    if any(
        not isinstance(movie_id, str) or not movie_id.strip()
        for movie_id in movie_ids
    ):
        raise ValueError("Movie IDs must be non-empty strings.")

    movie_ids = list(dict.fromkeys(movie_ids))

    if not movie_ids:
        return {}

    placeholders = ", ".join(["%s"] * len(movie_ids))

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            sql = f"""
                SELECT
                    m.movie_id,
                    m.title,

                    COALESCE(
                        (
                            SELECT GROUP_CONCAT(
                                g.genre_name
                                ORDER BY g.genre_name
                                SEPARATOR ' · '
                            )
                            FROM movie_genres AS mg
                            JOIN genres AS g
                                ON mg.genre_id = g.genre_id
                            WHERE mg.movie_id = m.movie_id
                        ),
                        ''
                    ) AS genres

                FROM movies AS m
                WHERE m.movie_id IN ({placeholders})
                ORDER BY m.title ASC
            """

            cursor.execute(sql, movie_ids)
            rows = cursor.fetchall()

        return {
            row["movie_id"]: row
            for row in rows
        }

    finally:
        connection.close()
