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

    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise ValueError("limit must be an integer between 1 and 100")

    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            if sort_by == "title_asc":
                order = "ASC"
            elif sort_by == "title_desc":
                order = "DESC"
            else:
                raise ValueError("Invalid sort_by option")

            query = f"""
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

                if genre_match == "all":
                    params.append(len(genres))
                else:
                    params.append(1)

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

                if actor_match == "all":
                    params.append(len(actors))
                else:
                    params.append(1)

            query += f"""
                ORDER BY m.title {order}, m.movie_id ASC
                LIMIT %s OFFSET %s
            """

            params.extend([limit, offset])

            cursor.execute(query, params)
            return list(cursor.fetchall())

    finally:
        connection.close()

