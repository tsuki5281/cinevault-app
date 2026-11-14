# Catalogue Module — API Reference

## 1. Overview

The catalogue module provides Python functions for retrieving movie details, searching movie titles, filtering by genres and actors, sorting results, and pagination.

**Files:**
- `db/mariadb.py` — Shared MariaDB connection helper
- `db/catalogue.py` — Catalogue browsing and movie details
- `tests/test_catalogue.py` — Automated catalogue validation tests

All catalogue functions access the local MariaDB database and return Python dictionaries or lists of dictionaries for use by other application modules.

## 2. Database Connection

### `get_connection()`

**Location:** `db/mariadb.py`

Creates a MariaDB connection using PyMySQL. Credentials are loaded from the project's `.env` file.

The connection uses `DictCursor`, allowing SQL results to be accessed using column names.

```python
from db.mariadb import get_connection

connection = get_connection()

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM movies")
        print(cursor.fetchone())
finally:
    connection.close()
```

**Note:** The caller is responsible for closing connections created directly through `get_connection()`.

## 3. Movie Details

### `get_movie_details(movie_id)`

Retrieves complete information for one movie.

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `movie_id` | str | Unique movie identifier |

**Returns**

A dictionary containing:
- `movie_id`
- `title`
- `director`
- `country`
- `description`
- `genres` — list of genre names
- `actors` — list of actor names

Returns `None` if the movie ID does not exist.

**Example**

```python
from db.catalogue import get_movie_details

movie = get_movie_details("s10")

if movie:
    print(movie["title"])
    print(movie["genres"])
    print(movie["actors"])
else:
    print("Movie not found.")
```

## 4. Catalogue Browsing

### `browse_movies()`

Searches and filters the movie catalogue with optional sorting and pagination.

**Function signature**

```python
browse_movies(
    title=None,
    genres=None,
    actors=None,
    genre_match="all",
    actor_match="all",
    sort_by="title_asc",
    limit=50,
    offset=0
)
```

**Parameters**

| Parameter | Type | Description |
|---|---|---|
| `title` | str or None | Optional partial movie title |
| `genres` | list[str] or None | Selected genre names |
| `actors` | list[str] or None | Selected actor names |
| `genre_match` | str | `"all"` (AND) or `"any"` (OR) |
| `actor_match` | str | `"all"` (AND) or `"any"` (OR) |
| `sort_by` | str | `"title_asc"` or `"title_desc"` |
| `limit` | int | Maximum results, from 1 to 100 |
| `offset` | int | Number of results to skip (0 or greater) |

**Returns**

A list of dictionaries, each containing `movie_id` and `title`.

Returns an empty list `[]` when no movies match.

### Usage Examples

**Browse the catalogue**

```python
movies = browse_movies()
```

Returns the first 50 movies in ascending title order.

**Search by title**

```python
movies = browse_movies(title="love")
```

Returns movies with `"love"` in their title.

**Sort Z–A**

```python
movies = browse_movies(
    title="love",
    sort_by="title_desc"
)
```

**Filter by multiple genres (AND)**

```python
movies = browse_movies(
    genres=["Horror Movies", "Thrillers"],
    genre_match="all"
)
```

Returns movies containing both selected genres.

**Filter by multiple genres (OR)**

```python
movies = browse_movies(
    genres=["Horror Movies", "Thrillers"],
    genre_match="any"
)
```

Returns movies containing at least one selected genre.

**Filter by multiple actors**

```python
movies = browse_movies(
    actors=["Rajneesh Duggal", "Adah Sharma"],
    actor_match="all"
)
```

Returns movies containing both selected actors.

Use `actor_match="any"` to match at least one selected actor.

**Combine genres and actors**

```python
movies = browse_movies(
    genres=["Horror Movies", "Thrillers"],
    actors=["Rajneesh Duggal", "Adah Sharma"],
    genre_match="all",
    actor_match="all"
)
```

Both selected genres and both selected actors must match.

**Pagination**

```python
page_1 = browse_movies(limit=10, offset=0)
page_2 = browse_movies(limit=10, offset=10)
```

Returns separate pages of 10 movies.

## 5. Filtering Behaviour

- Multiple genres can use AND (`"all"`) or OR (`"any"`) matching.
- Multiple actors can independently use AND (`"all"`) or OR (`"any"`) matching.
- Genre and actor filters are combined using AND between filter groups.
- Title search can be combined with genre and actor filters.
- Sorting defaults to ascending title order.
- Empty genre or actor lists apply no filtering for that category.
- Duplicate names within an input list are removed.
- Invalid matching modes, sorting options, limits and offsets raise `ValueError`.

## 6. SQL Implementation

The catalogue uses:
- Parameterised SQL queries for safe input handling
- `JOIN` operations across junction tables
- Nested queries for filtering matching movie IDs
- `GROUP BY` and `HAVING COUNT(DISTINCT ...)` for multi-tag matching
- `ORDER BY` for sorting
- `LIMIT` and `OFFSET` for pagination

These features support flexible searching while avoiding duplicate movie results.

## 7. Integration Notes

### For Dhakshini — Ratings and Watchlist

Use `movie_id` from `browse_movies()` or `get_movie_details()` when linking movies to ratings or watchlist records.

The catalogue module does not modify ratings or watchlist data.

### For Nusrat — Streamlit UI

Import the functions:

```python
from db.catalogue import browse_movies, get_movie_details
```

Use `browse_movies()` to populate catalogue search results and `get_movie_details(movie_id)` to display a selected movie.

The UI should handle empty search results (`[]`), missing movies (`None`) and invalid inputs (`ValueError`).

For pagination, adjust `offset` according to the selected page and `limit`.

### For Weibin — MongoDB Reviews

Use the existing `movie_id` to associate review documents with movies in the MariaDB catalogue.

## 8. Local Setup

1. Install project dependencies, including `pymysql`, `python-dotenv` and `pandas`.
2. Ensure MariaDB is installed and running.
3. Create the database specified by `DB_NAME` in the local `.env` file.
4. Execute `sql/schema.sql` to create the required tables.
5. Ensure the cleaned catalogue CSV is available at `data/netflix_movies_cleaned.csv`.
6. Run the import script from the repository root:

```powershell
python -m scripts.import_movies
```

7. Run the catalogue tests:

```powershell
python -m tests.test_catalogue
```

The actual MariaDB data is not stored in GitHub; each team member must initialise their own local database.

## 9. Testing Results

The catalogue module was tested against 4,677 imported movies.

| Test Case | Matches | Status |
|---|---:|---|
| Horror Movies AND Thrillers | 106 | PASS |
| Horror Movies OR Thrillers | 673 | PASS |
| Rajneesh Duggal AND Adah Sharma | 1 | PASS |
| Rajneesh Duggal OR Adah Sharma | 5 | PASS |
| Combined genre and actor AND filters | 1 | PASS |

Additional tests passed for movie details, title search, sorting, pagination, invalid parameters and empty results.

All completed catalogue tests passed.

## 10. Known Limitations

- The catalogue contains movies only; TV shows are excluded.
- Only columns retained during dataset cleaning are available.
- Sorting currently supports title A–Z and Z–A only.
- Pagination returns a maximum of 100 results per request.
- Community rating-based sorting is handled by the MariaDB ratings module rather than the catalogue module.
- Catalogue functions require an accessible MariaDB connection.

## 11. Streamlit Integration Updates

The catalogue module was extended to support the Streamlit Search interface. These additions allow the application to retrieve movie, actor and genre information dynamically from the existing MariaDB catalogue.

### Additional Functions

#### `get_search_suggestions(keyword, limit=5)`

Retrieves matching suggestions from three categories:
- Movies
- Actors
- Genres

Suggestions beginning with the entered keyword are prioritised before partial matches.

Returns a dictionary containing three lists: `movies`, `actors` and `genres`.

An empty keyword or an invalid limit raises `ValueError`. The limit must be between 1 and 20.

#### `get_recommended_actors(limit=12)`

Retrieves actor recommendations based on the curated collection of six demo movies.

The results include:
- `actor_id`
- `actor_name`
- `movie_count`
- `movie_id`
- `title`

Actors are ranked by their number of movie appearances across the catalogue, with alphabetical ordering used to break ties.

The function accepts a limit between 1 and 24.

#### `get_all_genres()`

Retrieves all available genre IDs and names from the `genres` table, ordered alphabetically.

This allows the Streamlit interface to populate genre selection controls dynamically instead of maintaining a hardcoded genre list.

#### `get_movie_card_details(movie_ids)`

Retrieves movie information required by the Search result cards in a single database query.

**Parameters**
- `movie_ids`: A list or tuple of movie IDs, with a maximum of 100 IDs.

**Returns**

A dictionary keyed by `movie_id`, containing:
- `movie_id`
- `title`
- `genres`

Duplicate movie IDs are removed. An empty input returns an empty dictionary `{}`. Invalid inputs raise `ValueError`.

Average ratings and rating counts are retrieved separately through the MariaDB ratings module.

### Updates to `browse_movies()`

The function now accepts `limit=None` to retrieve all matching movie IDs without applying SQL pagination. When `limit=None`, `offset` must be zero.

This supports the Streamlit application's Highest Rated sorting workflow. The catalogue first retrieves all movies matching the selected title, actor and genre filters. Their rating-based ranking is subsequently handled by `db.mariadb.get_movies_sorted_by_rating()`.

The existing title sorting, actor and genre filtering, Any/All matching and normal pagination behaviour are retained.