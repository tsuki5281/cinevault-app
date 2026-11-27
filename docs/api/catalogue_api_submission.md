# Catalogue Module — API Reference

## 1. Overview

The CineVault catalogue module provides movie retrieval, title search, multi-tag genre and actor filtering, sorting, pagination, and data retrieval for the Streamlit interface. It uses MariaDB through PyMySQL.

| File | Purpose |
|---|---|
| `db/catalogue.py` | Catalogue queries and supporting search functions |
| `db/mariadb.py` | MariaDB connection helper and rating-related operations |
| `tests/test_catalogue.py` | Automated catalogue validation tests |

## 2. Database Connection

### `get_connection()`

**Module:** `db/mariadb.py`

Opens a MariaDB connection using credentials from the local `.env` file. PyMySQL's `DictCursor` allows query results to be accessed by column name. Connections opened directly by callers must be closed after use.

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

## 3. Movie Details

### `get_movie_details(movie_id)`

Returns a single movie's information, including associated genres and actors.

| Parameter | Type | Description |
|---|---|---|
| `movie_id` | `str` | Unique movie identifier (e.g. `"s10"`) |

**Return:** A dictionary with `movie_id`, `title`, `director`, `country`, `description`, `genres` (list), and `actors` (list), or `None` if the ID does not exist.

```python
from db.catalogue import get_movie_details

movie = get_movie_details("s10")
if movie is not None:
    print(movie["title"], movie["genres"], movie["actors"])
```

## 4. Catalogue Search and Browsing

### `browse_movies(...)`

Searches the catalogue using optional title, genre, and actor filters. Supports independent AND/OR selection for genres and actors, alphabetical sorting, and SQL pagination.

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

| Parameter | Accepted value | Description |
|---|---|---|
| `title` | `str` or `None` | Optional partial title search |
| `genres` | List of names or `None` | Selected genre tags |
| `actors` | List of names or `None` | Selected actor names |
| `genre_match` | `"all"` / `"any"` | Require every selected genre / at least one |
| `actor_match` | `"all"` / `"any"` | Require every selected actor / at least one |
| `sort_by` | `"title_asc"` / `"title_desc"` | Title sorting, A–Z / Z–A |
| `limit` | Integer 1–100, or `None` | Maximum results; `None` disables SQL pagination |
| `offset` | Non-negative integer | Number of matching results to skip; must be `0` when `limit=None` |

**Return:** A list of dictionaries containing `movie_id` and `title`; `[]` if no results match.

**Filter semantics:** `"all"` requires all tags within the selected category, whereas `"any"` requires at least one. If both genre and actor filters are supplied, the two categories are combined with AND. Empty lists apply no filter in that category. Repeated selected names are deduplicated. Invalid options or pagination inputs raise `ValueError`.

```python
from db.catalogue import browse_movies

# Search for a title, sorted Z–A
movies = browse_movies(title="love", sort_by="title_desc")

# Multi-genre and multi-actor AND matching
movies = browse_movies(
    genres=["Horror Movies", "Thrillers"],
    actors=["Rajneesh Duggal", "Adah Sharma"],
    genre_match="all",
    actor_match="all"
)

# Ten results per page
page_1 = browse_movies(limit=10, offset=0)
page_2 = browse_movies(limit=10, offset=10)

# Retrieve all matching IDs for subsequent rating-based ranking
all_matches = browse_movies(genres=["Thrillers"], limit=None, offset=0)
```

For the Streamlit *Highest Rated* workflow, `browse_movies(limit=None, offset=0)` retrieves all matching catalogue entries without SQL pagination; `db.mariadb.get_movies_sorted_by_rating()` then handles the rating-based order. Normal browsing retains title sorting and pagination.

## 5. Additional Search Functions

### `get_search_suggestions(keyword, limit=5)`

Returns a dictionary containing three suggestion lists: `movies`, `actors`, and `genres`. Suggestions starting with the keyword are prioritised before other partial matches. An empty keyword or limit outside 1–20 raises `ValueError`.

### `get_recommended_actors(limit=12)`

Returns recommended actors using a curated set of six demo movies, ranked by their appearances across the catalogue and then alphabetically. Each result includes `actor_id`, `actor_name`, `movie_count`, `movie_id`, and `title`. The accepted limit is 1–24.

### `get_all_genres()`

Returns available genre IDs and names in alphabetical order for dynamically populated genre selections.

### `get_movie_card_details(movie_ids)`

Retrieves search-result card data for up to 100 movie IDs in one query. Accepts a list or tuple, removes duplicate IDs, and returns a dictionary keyed by `movie_id`; each entry includes `movie_id`, `title`, and `genres`. An empty input returns `{}`; invalid inputs raise `ValueError`.

Average ratings and rating counts are obtained separately from the MariaDB ratings module.

## 6. SQL Techniques

The catalogue queries use:

- **Parameterised queries** for safe insertion of search values.
- **JOINs** to retrieve related actor and genre information through junction tables.
- **Nested subqueries** to select movies matching genre and actor criteria.
- **`GROUP BY` with `HAVING COUNT(DISTINCT ...)`** to implement multi-tag AND/OR matching without duplicate movie results.
- **`ORDER BY`, `LIMIT`, and `OFFSET`** for alphabetical sorting and pagination.

These operations allow flexible searches while preserving the relational structure of the catalogue.

## 7. Testing and Validation

The catalogue was tested against **4,677 imported movies**. The comprehensive tests independently compared SQL filtering results with each movie's stored genre and actor associations.

| Filter | Matching movies | Result |
|---|---:|---|
| Horror Movies AND Thrillers | 106 | PASS |
| Horror Movies OR Thrillers | 673 | PASS |
| Rajneesh Duggal AND Adah Sharma | 1 | PASS |
| Rajneesh Duggal OR Adah Sharma | 5 | PASS |
| Both genres AND both actors | 1 | PASS |

Tests also covered movie details, title search, sorting, pagination, invalid inputs, and empty results. These results refer to the original catalogue validation; the subsequent Streamlit helper functions are documented above, but no separate test results for them are asserted here.

Run the catalogue test suite from the repository root:

```powershell
python -u -m tests.test_catalogue
```

The full verification performs thousands of database queries and is intended for development validation rather than routine application startup.

## 8. Scope and Limitations

- The catalogue includes movies only; TV shows were excluded during cleaning.
- Only attributes retained in the cleaned dataset are available.
- Catalogue-level sorting supports title A–Z and Z–A; rating-based ranking is implemented separately by the MariaDB ratings module.
- Standard paginated queries accept 1–100 results per call; `limit=None` is reserved for unpaginated retrieval.
- Functions require an accessible MariaDB database populated with the cleaned catalogue.

For complete application setup, including MariaDB, MongoDB, and launching Streamlit, refer to the repository's main `README.md`.
