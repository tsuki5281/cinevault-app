-- Adavanced SQL queries for Netflix Review App

-- Query 1: Highest-Rated Movies
-- Combines movies and ratings using JOIN
-- Calculates average ratings and rating counts
-- HAVING filters movies with at least 2 ratings
-- Results are sorted by average rating

SELECT
    m.movie_id,
    m.title,
    AVG(r.stars) AS average_rating,
    COUNT(r.user_id) AS rating_count
FROM movies AS m
JOIN ratings AS r
    ON m.movie_id = r.movie_id
GROUP BY m.movie_id, m.title
HAVING COUNT(r.user_id) >= 2
ORDER BY average_rating DESC, rating_count DESC
LIMIT 10;


-- Query 2: Movie Rating Statistics
-- Displays the average, total, highest and lowest ratings for each movie
-- LEFT JOIN includes movies even if they have not received any ratings
-- Uses AVG(), COUNT(), MAX() and MIN()

SELECT
    m.movie_id,
    m.title,
    AVG(r.stars) AS average_rating,
    COUNT(r.user_id) AS rating_count,
    MAX(r.stars) AS highest_rating,
    MIN(r.stars) AS lowest_rating
FROM movies AS m
LEFT JOIN ratings AS r
    ON m.movie_id = r.movie_id
GROUP BY m.movie_id, m.title
ORDER BY average_rating DESC, rating_count DESC;


-- Query 3: Movie Rating Summary View
-- Creates a view that summarises the ratings for each movie
-- LEFT JOIN includes movies even if they have not received any ratings
-- Uses COUNT() and ROUND(AVG()) to show the rating count and average stars

CREATE OR REPLACE VIEW movie_rating_summary AS
SELECT
    m.movie_id,
    m.title,
    COUNT(r.stars) AS rating_count,
    ROUND(AVG(r.stars), 2) AS avg_stars
FROM movies AS m
LEFT JOIN ratings AS r
    ON m.movie_id = r.movie_id
GROUP BY m.movie_id, m.title;


-- Query 4: Movies Rated Above Average
-- Lists movies whose average rating is higher than the average of all ratings
-- Nested query: the subquery in HAVING calculates the overall average stars
-- Results are sorted by average stars

SELECT
    m.movie_id,
    m.title,
    ROUND(AVG(r.stars), 2) AS avg_stars
FROM movies AS m
JOIN ratings AS r
    ON m.movie_id = r.movie_id
GROUP BY m.movie_id, m.title
HAVING AVG(r.stars) > (
    SELECT AVG(stars)
    FROM ratings
)
ORDER BY avg_stars DESC;
