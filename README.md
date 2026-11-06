# netflix-review-app

**INF2003 Database Systems Group Project**

A Netflix-inspired movie catalogue application integrating MariaDB and MongoDB.

## Project Overview

The application allows users to browse and search movies, filter by genres and actors, view movie details, manage ratings and watchlists, and submit reviews.

### Main Features

- **Movie Catalogue:** Search movies by title and filter by multiple genres and actors using AND/OR matching.
- **Sorting and Pagination:** Sort movies alphabetically and navigate through results.
- **Movie Details:** View directors, cast, country, descriptions and genres.
- **Ratings:** Rate movies on a 1–5 star scale.
- **Watchlist:** Save and manage movies in a personal watchlist.
- **Reviews:** Store and retrieve movie reviews using MongoDB.

*Note: Some features are still under development.*

## Technologies

- Python
- MariaDB
- MongoDB
- PyMySQL
- PyMongo
- Streamlit
- pandas
- python-dotenv

## Project Structure

```text
netflix-review-app/
├── data/                  # Original and cleaned datasets
├── db/
│   ├── mariadb.py         # MariaDB connection, ratings and watchlist operations
│   ├── mongodb.py         # MongoDB module
│   └── catalogue.py       # Catalogue browsing and movie details
├── docs/
│   ├── catalogue_api.md
│   ├── catalogue_test_results.md
│   ├── ratings_watchlist_api.md
│   ├── sql_test_results.md
│   ├── er_diagram.png
│   └── er_diagram.drawio
├── scripts/
│   └── import_movies.py
├── sql/
│   ├── schema.sql
│   ├── validate_catalogue.sql
│   └── advanced_queries.sql
├── tests/
│   ├── test_catalogue.py
│   └── test_ratings_watchlist.py
├── .env                   # Local credentials (not committed)
└── README.md
```

## Local Setup — MariaDB Catalogue

### 1. Clone the repository

Clone the GitHub repository and open its root directory in VS Code.

### 2. Install Python dependencies

Using an activated Python virtual environment:

```powershell
pip install pymysql python-dotenv pandas
```

Additional packages may be required for the MongoDB and Streamlit modules.

### 3. Configure environment variables

Create a `.env` file in the project root:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=netflix_review_db
```

Replace the example values with your local MariaDB credentials.

**Do not commit `.env` to GitHub.**

### 4. Create the MariaDB database

In HeidiSQL, create a database named `netflix_review_db`, then execute:

```text
sql/schema.sql
```

This creates the eight relational tables required by the application.

### 5. Import the movie catalogue

Ensure that `data/netflix_movies_cleaned.csv` exists.

Run the import script from the repository root:

```powershell
python scripts/import_movies.py
```

The catalogue contains 4,677 cleaned movie records, along with their genre and actor associations.

### 6. Run catalogue tests

From the repository root:

```powershell
python -m tests.test_catalogue
```

The tests verify movie retrieval, filtering, sorting, pagination and selected edge cases.

**Note:** The full-catalogue validation currently performs thousands of database queries and is intended for development verification rather than routine application startup.

## Ratings and Watchlist

The application supports movie ratings and personal watchlists through MariaDB.

- **Add ratings:** Users can rate movies from 1 to 5 stars.
- **Manage ratings:** Users can retrieve, update and delete their ratings.
- **Manage watchlists:** Users can add movies to and remove movies from their personal watchlists.
- **Rating summaries:** Calculate average ratings and rating counts for movies.
- **Highest-rated movies:** Retrieve movies based on their average ratings and minimum rating counts.

The ratings and watchlist operations include input validation and error handling to prevent invalid ratings, duplicate entries and references to non-existent users or movies.

For function details, see [`docs/ratings_watchlist_api.md`](docs/ratings_watchlist_api.md).

For SQL query examples and testing results, see [`docs/sql_test_results.md`](docs/sql_test_results.md).

## Using the Catalogue Functions

```python
from db.catalogue import browse_movies, get_movie_details

# Browse movies
movies = browse_movies()

# Search by title
movies = browse_movies(title="love")

# Filter by multiple genres
movies = browse_movies(
    genres=["Horror Movies", "Thrillers"],
    genre_match="all"
)

# Filter by multiple actors
movies = browse_movies(
    actors=["Rajneesh Duggal", "Adah Sharma"],
    actor_match="any"
)

# Combine filters
movies = browse_movies(
    genres=["Horror Movies", "Thrillers"],
    actors=["Rajneesh Duggal", "Adah Sharma"],
    genre_match="all",
    actor_match="all",
    limit=10
)

# View a movie
movie = get_movie_details("s10")
```

For full parameters, return formats and integration instructions, see [`docs/catalogue_api.md`](docs/catalogue_api.md).

## Database Design

MariaDB contains eight tables:

`movies`, `genres`, `actors`, `movie_genres`, `movie_actors`, `users`, `ratings` and `watchlist`.

The schema is defined in `sql/schema.sql`, and the ER diagram is available in `docs/er_diagram.png`.

MongoDB is used for review documents.

## Development Status

- **Catalogue foundation:** Implemented and tested.
- **Ratings and watchlist:** Implemented and tested.
- **MongoDB reviews:** Under development.
- **Streamlit interface:** Under development.

## Team Integration

The catalogue module uses `movie_id` as the unique movie identifier. Other modules should use the same ID when associating ratings, watchlist entries and MongoDB reviews with catalogue movies.

Each developer must initialise their own local database. The GitHub repository contains the schema and import scripts, not the populated MariaDB database itself.