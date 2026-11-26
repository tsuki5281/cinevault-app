
# Ratings and Watchlist Module (API Reference)

## 1. Overview

This module manages user ratings, watchlists, watched history and movie rating statistics for CineVault using MariaDB.

It provides the following functionalities:

- Add, retrieve, update and delete movie ratings.
- Add movies to a user's watchlist, retrieve saved movies and remove entries.
- Mark movies as watched, retrieve watched history and remove watched status.
- Retrieve a user's rating history.
- Calculate average ratings and total rating counts for movies.
- Retrieve rating distributions across all five star levels.
- Identify and retrieve the highest-rated movies based on user ratings.
- Retrieve rating summaries for multiple movies.
- Retrieve ratings submitted by multiple users for a specific movie.
- Sort a filtered list of movies based on their average ratings and rating counts.

**Files:**
- `db/mariadb.py`: Contains the MariaDB connection helper and database functions for ratings, watchlists, watched history and rating statistics.
- `sql/advanced_queries.sql`: Contains advanced SQL queries for movie rating analysis.
- `sql/watched_movies.sql`: Contains the SQL table definition for watched movie records.
- `docs/sql_test_results.md`: Records the SQL testing and verification results.


## 2. Ratings Management

### `add_rating(user_id, movie_id, stars)`

Adds a new rating for a movie by a specific user.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | int | ID of the user giving the rating |
| `movie_id` | str | ID of the movie being rated |
| `stars` | int | Rating given by the user (1 to 5) |

**Returns**
- `True` if the rating is added successfully.
- `False` if the user has already rated the same movie.
- Raises `ValueError` if the user ID or movie ID does not exist.
- Raises `ValueError` if the rating is not an integer between 1 and 5.

**Example**

```python
from db.mariadb import add_rating

result = add_rating(1, "s10", 4)
print(result)
```

### `get_rating(user_id, movie_id)`

Retrieves the rating given by a specific user for a movie.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | int | ID of the user |
| `movie_id` | str | ID of the movie |

**Returns**

A dictionary containing:
- `stars`
- `updated_at`

Returns `None` if the user has not rated the movie.

**Example**

```python
from db.mariadb import get_rating

rating = get_rating(1, "s10")

if rating:
    print(rating["stars"])
else:
    print("No rating found.")
```

### `update_rating(user_id, movie_id, stars)`

Updates an existing rating given by a user.

The new rating must be an integer between 1 and 5.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | int | ID of the user |
| `movie_id` | str | ID of the movie |
| `stars` | int | New rating (1 to 5) |

**Returns**
- `True` if the rating is updated successfully.
- `False` if the rating does not exist.
- Raises `ValueError` if the rating is not an integer between 1 and 5.

**Example**

```python
from db.mariadb import update_rating

result = update_rating(1, "s10", 5)
print(result)
```

### `delete_rating(user_id, movie_id)`

Deletes a user's rating for a specific movie.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | int | ID of the user |
| `movie_id` | str | ID of the movie |

**Returns**
- `True` if the rating is deleted successfully.
- `False` if the rating does not exist.

**Example**

```python
from db.mariadb import delete_rating

result = delete_rating(1, "s10")
print(result)
```

## 3. Watchlist Management

### `add_to_watchlist(user_id, movie_id)`

Adds a movie to a specific user's watchlist.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | int | ID of the user |
| `movie_id` | str | ID of the movie |

**Returns**
- `True` if the movie is added successfully.
- `False` if the movie is already in the user's watchlist.
- Raises `ValueError` if the user ID or movie ID does not exist.

**Example**

```python
from db.mariadb import add_to_watchlist

result = add_to_watchlist(1, "s10")
print(result)
```

### `get_watchlist(user_id)`

Retrieves all movies saved in a specific user's watchlist.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | int | ID of the user |

**Returns**

A list of dictionaries containing:
- `movie_id`
- `title`
- `added_at`

Returns an empty list `[]` if the watchlist has no entries.

**Example**

```python
from db.mariadb import get_watchlist

movies = get_watchlist(1)

for movie in movies:
    print(movie["title"])
```

### `remove_from_watchlist(user_id, movie_id)`

Removes a movie from a specific user's watchlist.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `user_id` | int | ID of the user |
| `movie_id` | str | ID of the movie |

**Returns**
- `True` if the movie is removed successfully.
- `False` if the movie is not in the user's watchlist.

**Example**

```python
from db.mariadb import remove_from_watchlist

result = remove_from_watchlist(1, "s10")
print(result)
```
## 4. Watched History Management

Watched history was introduced as an additional user activity feature using a separate MariaDB table named `watched_movies`.

#### `mark_as_watched(user_id, movie_id)`

Records that a user has watched a particular movie.

**Returns**
- `True` if the record is added successfully.
- `False` if the user has already marked the movie as watched.
- Raises `ValueError` if the user ID or movie ID does not exist.

#### `get_watched_movies(user_id)`

Retrieves all movies marked as watched by a specific user.

**Returns**

A list of dictionaries containing:
- `movie_id`
- `title`
- `watched_at`

Results are ordered by the most recently watched movie.

#### `remove_watched_status(user_id, movie_id)`

Removes a movie from a user's watched history.

**Returns**
- `True` if a record is deleted successfully.
- `False` if the record does not exist.

Removing a watched record does not delete the user's rating or review.


## 5. Rating Summaries and Advanced SQL
This section covers the retrieval, calculation and analysis of movie ratings using MariaDB. It includes aggregate functions, JOIN operations, grouping, filtering and batch retrieval.

### `get_average_rating(movie_id)`

Calculates the average rating submitted by users for a specific movie.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `movie_id` | str | ID of the movie |

**Returns**

The average rating as a decimal value.

Returns `None` if the movie has no ratings.

**Example**

```python
from db.mariadb import get_average_rating

average = get_average_rating("s10")
print(average)
```

### `get_rating_count(movie_id)`

Counts the total number of ratings received by a specific movie.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `movie_id` | str | ID of the movie |

**Returns**

An integer representing the total number of ratings.

Returns `0` if the movie has no ratings.

**Example**

```python
from db.mariadb import get_rating_count

count = get_rating_count("s10")
print(count)
```

### `get_highest_rated_movies(minimum_ratings=2, limit=10)`

Retrieves the highest-rated movies based on their average user ratings.

The function allows a minimum number of ratings to be set so that movies with very few ratings can be excluded from the results.

**Function signature**

```python
get_highest_rated_movies(
    minimum_ratings=2,
    limit=10
)
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `minimum_ratings` | int | Minimum number of ratings a movie must have. Defaults to 2. |
| `limit` | int | Maximum number of movies to return. Defaults to 10. |

Both parameters must be positive integers. Invalid values raise `ValueError`.

**Returns**

A list of dictionaries containing:
- `movie_id`
- `title`
- `average_rating`
- `rating_count`

Returns an empty list if no movies meet the minimum rating requirement.

**Example**

```python
from db.mariadb import get_highest_rated_movies

movies = get_highest_rated_movies(
    minimum_ratings=2,
    limit=10
)

for movie in movies:
    print(
        movie["title"],
        movie["average_rating"],
        movie["rating_count"]
    )
```
#### `get_rating_distribution(movie_id)`

Retrieves the number of ratings received at each star level for a specific movie.

**Parameters**
- `movie_id`: String representing the movie ID.

**Returns**

A dictionary containing all five rating levels (1 to 5), including levels with zero ratings.

Example:

    {
        1: 0,
        2: 1,
        3: 2,
        4: 3,
        5: 1
    }

This function supports displaying the distribution of community ratings.

**SQL features used**

- `JOIN` combines movie details with their ratings.
- `AVG()` calculates the average rating.
- `COUNT()` counts the number of ratings.
- `GROUP BY` groups the ratings by movie.
- `HAVING` filters movies based on their rating count.
- `ORDER BY` sorts the movies by their average rating and rating count.
- `LIMIT` controls the number of results returned.

#### `get_user_ratings(user_id)`

Retrieves all movie ratings submitted by a specific user.

**Parameters**
- `user_id`: Integer representing the user's ID.

**Returns**

A list of dictionaries containing:
- `movie_id`
- `title`
- `stars`
- `updated_at`

Results are ordered by the most recently updated rating.

This function supports the My Activity page, allowing users to view their personal rating history.

### 5.2 Batch Rating Retrieval Functions

The following functions were introduced to support efficient integration between the catalogue, ratings and review modules.

#### `get_movie_rating_summaries(movie_ids)`

Retrieves average ratings and rating counts for multiple movies in batches.

**Parameters**
- `movie_ids`: A list or tuple of movie IDs.

**Returns**

A dictionary keyed by `movie_id`, containing:
- `average_rating`
- `rating_count`

Example:

    {
        "s10": {
            "average_rating": 4.5,
            "rating_count": 4
        },
        "s101": {
            "average_rating": None,
            "rating_count": 0
        }
    }

Movies without ratings are included with `average_rating=None` and `rating_count=0`.

Duplicate movie IDs are removed. An empty input returns an empty dictionary `{}`. Invalid inputs raise `ValueError`.

The function processes movie IDs in batches of up to 500 per database query.

This function is used by the Streamlit Search interface to display community ratings on movie cards without performing a separate rating query for every movie.

#### `get_movie_user_ratings(movie_id, user_ids)`

Retrieves star ratings given by multiple users for a specific movie using batched database queries.

**Parameters**
- `movie_id`: String representing the movie ID.
- `user_ids`: A list or tuple of positive integer user IDs.

**Returns**

A dictionary keyed by `user_id`, with the corresponding star rating as the value.

Example:

    {
        40: 5,
        36: 4,
        38: 3
    }

Users who have not rated the movie are omitted from the result.

Duplicate user IDs are removed. An empty user ID list returns an empty dictionary `{}`. Invalid inputs raise `ValueError`.

The function processes user IDs in batches of up to 500 per database query.

This function supports the retrieval of reviewer ratings for community review cards without requiring an individual database query for every review.

#### `get_movies_sorted_by_rating(movie_ids)`

Ranks an existing list of filtered movie IDs according to their community ratings.

**Parameters**
- `movie_ids`: A list or tuple of movie IDs.

**Returns**

A list of dictionaries containing:
- `movie_id`
- `title`
- `average_rating`
- `rating_count`

The ranking order is:
1. Movies with ratings appear before unrated movies.
2. Higher average ratings appear first.
3. Higher rating counts are used to break equal-average ties.
4. Movie titles are used as the next tie-breaker.
5. Movie IDs provide the final deterministic ordering.

The function removes duplicate movie IDs and processes them in batches of up to 500. An empty input returns an empty list `[]`.

The Streamlit Search interface uses this function after catalogue filtering to ensure that Highest Rated sorting is applied across all matching movies before displaying paginated results.

## 6. Error Handling and Validation

The MariaDB module implements input validation and database error handling to maintain data integrity and ensure that invalid or duplicate entries are handled appropriately.

**Rating Validation**

The `add_rating()` and `update_rating()` functions validate that ratings are integers between 1 and 5. Invalid values raise a `ValueError`.

**Duplicate Entry Handling**

Duplicate entries are handled using database integrity constraints. If a duplicate rating or watchlist entry is detected, the corresponding function returns False.

**Foreign Key Validation**

Foreign key constraints ensure that ratings, watchlist entries and watched-history records reference valid users and movies. Invalid references raise ValueError.

**Database error handling**

The add_rating(), add_to_watchlist() and mark_as_watched() functions handle MariaDB integrity errors using the following error codes:

| Error Code | Meaning | Behaviour |
|---|---|---|
| 1062 | Duplicate entry | Returns `False` |
| 1452 | Foreign key constraint failure | Raises `ValueError` |
| Other | Unexpected integrity error | Raises the original exception |

If an insertion fails, `connection.rollback()` is used to undo the unsuccessful operation.

**Database constraints**

The existing database schema already includes the following constraints:

- Composite primary keys prevent the same user from rating or adding the same movie to their watchlist more than once.
- Foreign keys ensure that the user and movie IDs exist in their respective tables.
- The `CHECK` constraint restricts movie ratings to values between 1 and 5.
- The `watched_movies` table uses a composite primary key to prevent the same movie from being marked as watched more than once by the same user.

## 7. SQL Implementation

The MariaDB module uses different SQL statements depending on the database operation:

- `INSERT` to add ratings, watchlist entries and watched-history records.
- `SELECT` to retrieve ratings, movie details, watchlist records and watched history.
- `UPDATE` to modify existing movie ratings.
- `DELETE` to remove ratings, watchlist entries and watched-history records.
- `JOIN` to combine movie information with related ratings, watchlist entries and user activity.
- `LEFT JOIN` to retrieve movie rating statistics while retaining movies that have no ratings.
- Aggregate functions such as `AVG()`, `COUNT()`, `MAX()` and `MIN()` to calculate movie rating statistics.
- `GROUP BY` to group rating records by movie or star level.
- `HAVING` to filter movies based on their total number of ratings.
- `ORDER BY` to arrange retrieved records according to rating dates or rating values.
- `LIMIT` to restrict the number of results returned by the highest-rated movies query.

Parameterised SQL queries are used when passing values into the database to support safer query execution.

For functions that retrieve rating information for multiple movies or users, identifiers are processed in batches of up to 500 per database query. The `get_movies_sorted_by_rating()` function performs its final sorting in Python after retrieving the rating information from MariaDB.

These SQL operations allow CineVault to manage user activity, retrieve movie information and analyse community ratings while maintaining data integrity.

## 8. Integration Notes

### For Member 1 — Catalogue

The existing `movie_id` returned by `browse_movies()` or `get_movie_details()` can be used when adding ratings or movies to a watchlist.

The ratings and watchlist functions do not modify the movie catalogue.

### For Nusrat — Streamlit UI

Import the required functions from `db.mariadb`:

```python
from db.mariadb import (
    add_rating,
    get_rating,
    update_rating,
    delete_rating,
    get_average_rating,
    get_rating_count,
    get_rating_distribution,
    get_highest_rated_movies,
    add_to_watchlist,
    get_watchlist,
    remove_from_watchlist,
    mark_as_watched,
    get_watched_movies,
    remove_watched_status,
    get_user_ratings,
    get_movie_rating_summaries,
    get_movie_user_ratings,
    get_movies_sorted_by_rating
)

```
### Integration with the Streamlit Application

The MariaDB module supplies numerical rating information and user movie activity to the Streamlit interface.

The integration supports:

- Displaying average community ratings and rating counts on Search movie cards.
- Sorting filtered movie results by community rating.
- Displaying individual users' ratings alongside their written reviews.
- Showing personal ratings in My Activity.
- Managing watched history independently from ratings and reviews.
- Maintaining user-specific watchlists and activity records.

The Streamlit layer combines catalogue, rating and review information for display while keeping the corresponding database operations within their respective modules.

The UI can use these functions to:
- Allow users to submit, retrieve, update and delete movie ratings.
- Display a user's existing ratings and personal rating history.
- Calculate and display average ratings and total rating counts.
- Display rating distributions across all five star levels.
- Retrieve and sort movies according to their community ratings.
- Allow users to add or remove movies from their watchlist.
- Display movies saved in a user's watchlist.
- Mark movies as watched and manage watched history.
- Retrieve individual user ratings associated with movie reviews.

The UI should handle `True` and `False` return values and catch `ValueError` exceptions to display suitable messages.

### For Weibin — MongoDB Reviews

The same `movie_id` from the MariaDB catalogue should be used when linking MongoDB review documents to movies.

The ratings and watchlist module only handles data stored in MariaDB and does not modify MongoDB reviews.

## 9. Local Setup

1. Install the required dependencies, including `pymysql` and `python-dotenv`.
2. Make sure MariaDB is installed and running.
3. Configure the database credentials in the local `.env` file.
4. Create the database specified by `DB_NAME`.
5. Execute `sql/schema.sql` if the database has not been set up yet.
6. Execute `sql/watched_movies.sql` to create the `watched_movies` table required for recording users' watched movies.
7. Import the movie catalogue by running:

```powershell
python -m scripts.import_movies
```

8. Make sure the required test users exist in the `users` table.
9. Import the required functions from `db.mariadb` when using the ratings and watchlist features.

**Note:** The database records are stored locally and are not automatically included in GitHub. Each team member needs to set up their own local MariaDB database.

## 10. Testing Results

The ratings and watchlist functions were tested using the local MariaDB database.

The tests covered:

- Adding, retrieving, updating and deleting ratings.
- Invalid rating values such as 0, 6 and negative numbers.
- Adding duplicate ratings for the same user and movie.
- Testing invalid user IDs and movie IDs.
- Updating and deleting ratings that do not exist.
- Adding and retrieving movies from the watchlist.
- Adding duplicate watchlist entries.
- Testing invalid user IDs and movie IDs for watchlist operations.
- Removing movies that are not in the watchlist.
- Calculating average ratings and rating counts.
- Retrieving the highest-rated movies.
- Testing invalid `minimum_ratings` and `limit` values.

The detailed SQL query testing results are recorded separately in `docs/sql_test_results.md`.

## 11. Known Limitations

- Each user can only have one rating for each movie.
- Each movie can only appear once in a user's watchlist.
- Ratings are restricted to whole numbers from 1 to 5.
- The highest-rated movies function uses a default minimum of two ratings and returns up to ten movies.
- The functions require an active connection to the local MariaDB database.
- The ratings and watchlist records are managed separately from the MongoDB movie reviews.
- Each user can only mark a particular movie as watched once.
- Batch rating retrieval functions process movie or user IDs in groups of up to 500 per database query.