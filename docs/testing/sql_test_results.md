
# Advanced SQL Queries — Testing Results

## 1. Overview

This document records the advanced SQL queries implemented and tested for CineVault using MariaDB.

The queries focus on analysing movie ratings and retrieving useful information from the movie catalogue.

Both queries were executed using HeidiSQL to check whether the results were correct.

## 2. Highest-Rated Movies

### Purpose

This query retrieves the highest-rated movies based on their average user ratings.

It only includes movies that have received at least two ratings and returns the top 10 results.

### SQL Query

```sql
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
```

### SQL Features Used

| SQL Feature | Purpose |
|---|---|
| JOIN | Combines movie information with its ratings. |
| AVG() | Calculates the average rating for each movie. |
| COUNT() | Counts the number of ratings received. |
| GROUP BY | Groups ratings according to each movie. |
| HAVING | Includes only movies with at least two ratings. |
| ORDER BY | Sorts movies by average rating and rating count. |
| LIMIT | Restricts the results to 10 movies. |

### Testing Results

The query was executed in HeidiSQL using the existing movie and rating records.

**Test movie:** `s10` (1920)

| Movie ID | Title | Average Rating | Rating Count |
|---|---|---:|---:|
| s10 | 1920 | 3.6667 | 3 |

**Result: PASS**

The query successfully returned the movie with its calculated average rating and total number of ratings.

## 3. Movie Rating Statistics

### Purpose

This query retrieves rating statistics for all movies in the catalogue.

It calculates the average, total, highest and lowest ratings for each movie.

A LEFT JOIN is used so that movies without any ratings are also included in the results.

### SQL Query

```sql
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
```

### SQL Features Used

| SQL Feature | Purpose |
|---|---|
| LEFT JOIN | Includes all movies, even those without ratings. |
| AVG() | Calculates the average rating. |
| COUNT() | Counts the total number of ratings. |
| MAX() | Retrieves the highest rating. |
| MIN() | Retrieves the lowest rating. |
| GROUP BY | Groups the results by movie. |
| ORDER BY | Sorts the results by average rating and rating count. |

### Testing Results

The query was executed successfully in HeidiSQL.

**Observed results:**

| Validation | Result |
|---|---:|
| Total movies returned | 4,677 |
| Movie tested | s10 (1920) |
| Number of ratings | 3 |
| Average rating | 3.6667 |
| Highest rating | 5 |
| Lowest rating | 2 |

The query also returned movies without ratings.

For movies without ratings:
- Average rating: NULL
- Rating count: 0
- Highest rating: NULL
- Lowest rating: NULL

**Result: PASS**

The query successfully returned rating statistics for both rated and unrated movies.

## 4. Overall Testing Summary

| Test Case | Expected Result | Status |
|---|---|---|
| Highest-rated movies query | Returns movies with at least two ratings | PASS |
| Average rating calculation | Calculates the correct average | PASS |
| Rating count calculation | Returns the correct number of ratings | PASS |
| Movie rating statistics | Returns average, count, highest and lowest ratings | PASS |
| LEFT JOIN functionality | Includes movies without ratings | PASS |
| HAVING condition | Excludes movies with fewer than two ratings | PASS |

## 5. Conclusion

Both advanced SQL queries were successfully implemented and tested using MariaDB.

The queries demonstrate the use of JOIN operations, aggregate functions, grouping, filtering and sorting to retrieve useful information from the movie catalogue and ratings database.

These queries provide additional rating analysis beyond the basic CRUD operations implemented for the application.
