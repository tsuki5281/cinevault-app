-- Check movies without genre or actor associations
SELECT
    'Movies without genres' AS validation_check,
    COUNT(*) AS missing_count
FROM movies m
WHERE NOT EXISTS (
    SELECT 1
    FROM movie_genres mg
    WHERE mg.movie_id = m.movie_id
)

UNION ALL

SELECT
    'Movies without actors',
    COUNT(*)
FROM movies m
WHERE NOT EXISTS (
    SELECT 1
    FROM movie_actors ma
    WHERE ma.movie_id = m.movie_id
);

-- Check duplicate movie IDs and missing movie information
SELECT
    COUNT(*) AS total_movies,
    COUNT(DISTINCT movie_id) AS unique_movie_ids,
    SUM(
        title IS NULL OR
        director IS NULL OR
        country IS NULL OR
        description IS NULL
    ) AS incomplete_movies
FROM movies;

-- Check duplicate movie-genre associations
SELECT
    'Duplicate movie-genre pairs' AS validation_check,
    COUNT(*) AS duplicate_count
FROM (
    SELECT movie_id, genre_id
    FROM movie_genres
    GROUP BY movie_id, genre_id
    HAVING COUNT(*) > 1
) AS duplicate_genres

UNION ALL

-- Check duplicate movie-actor associations
SELECT
    'Duplicate movie-actor pairs',
    COUNT(*)
FROM (
    SELECT movie_id, actor_id
    FROM movie_actors
    GROUP BY movie_id, actor_id
    HAVING COUNT(*) > 1
) AS duplicate_actors;

-- Check for invalid movie-genre references
SELECT
    'Invalid movie-genre references' AS validation_check,
    COUNT(*) AS invalid_count
FROM movie_genres mg
LEFT JOIN movies m ON mg.movie_id = m.movie_id
LEFT JOIN genres g ON mg.genre_id = g.genre_id
WHERE m.movie_id IS NULL OR g.genre_id IS NULL

UNION ALL

-- Check for invalid movie-actor references
SELECT
    'Invalid movie-actor references',
    COUNT(*)
FROM movie_actors ma
LEFT JOIN movies m ON ma.movie_id = m.movie_id
LEFT JOIN actors a ON ma.actor_id = a.actor_id
WHERE m.movie_id IS NULL OR a.actor_id IS NULL;