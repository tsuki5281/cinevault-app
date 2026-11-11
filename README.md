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
│   ├── mongodb.py         # MongoDB reviews: CRUD, browsing, advanced queries
│   └── catalogue.py       # Catalogue browsing and movie details
├── docs/
│   ├── catalogue_api.md
│   ├── reviews_api.md
│   ├── mongodb_model.md
│   ├── mongodb_handover.md
│   ├── review_dataset_notes.md
│   ├── advanced_query_results.md
│   ├── mongodb_test_results.md
│   ├── catalogue_test_results.md
│   ├── ratings_watchlist_api.md
│   ├── sql_test_results.md
│   ├── er_diagram.png
│   └── er_diagram.drawio
├── scripts/
│   ├── import_movies.py
│   ├── init_mongodb.py
│   ├── convert_reviews_to_mongo.py
│   ├── convert_movies_to_mongo.py
│   ├── tag_reviews.py
│   └── performance_mongodb.py
├── sql/
│   ├── schema.sql
│   ├── validate_catalogue.sql
│   └── advanced_queries.sql
├── tests/
│   ├── test_catalogue.py
│   ├── test_ratings_watchlist.py
│   └── test_reviews.py
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

## Local Setup: MongoDB Reviews (Weibin)

This is the part of the app where users write reviews, mark spoilers and tag what a movie is like (funny, scary, slow...). Reviews live in MongoDB instead of MariaDB because each one is a different length and carries its own list of tags, which fits a document better than a table row.

Do the MariaDB setup above first. Every review points to a MariaDB user and movie, so the catalogue needs to be there before any reviews can be loaded. The whole thing takes about 5 minutes.

### 1. Install the tools

Everything you need (MongoDB Community Server, MongoDB Compass and PyMongo) is listed in the **Software Setup** checklist in our team tracker, with download links and a quick check for each. Once those show "Done" for you, carry on here.

### 2. Add MongoDB settings to `.env`

**Where:** VS Code. Open the `.env` file in the project folder and add these two lines under your MariaDB settings. A local MongoDB doesn't need a password, so there's nothing secret here:

```text
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=netflix_review_db
```

### 3. Create the collection and load the reviews

**Where:** Command Prompt (cmd). Open it, go to the project folder first, then run these in order:

```powershell
cd C:\path\to\netflix-review-app
```

```powershell
python -m scripts.init_mongodb
python -m scripts.convert_reviews_to_mongo
python -m scripts.convert_movies_to_mongo
```

What each one does:
- `init_mongodb` creates the `reviews` collection and its rules, e.g. one review per user per movie, and no empty reviews.
- `convert_reviews_to_mongo` loads our 144 sample reviews for the first 100 movies from `data/reviews.csv`. It checks every row first and tells you if one is skipped.
- `convert_movies_to_mongo` copies the catalogue into MongoDB so the stats can show movie titles.

The commands are safe to run again. Rerunning the review loader replaces the sample reviews but keeps any reviews written in the app.

### 4. Run review tests

**Where:** the same Command Prompt window, still in the project folder.

```powershell
python -m tests.test_reviews
```

If you see `Ran 14 tests` and `OK`, you're good to go. The tests clean up after themselves, so they won't leave fake users or reviews behind.

**Want to see the data?** Open **MongoDB Compass** → connect to `mongodb://localhost:27017` → `netflix_review_db` → `reviews`. You should see 144 documents, and the **Indexes** tab shows `uniq_user_movie` and `movie_newest`.

### 5. Add a review manually (optional)

Handy for testing before the Streamlit page is ready.

**First, find a user ID.** Open HeidiSQL, connected to `netflix_review_db`:

```sql
SELECT user_id, username FROM users;
```

**Option A (recommended). Where:** Command Prompt, in the project folder. Change the user ID, movie ID and text to your own:

```powershell
python -c "from db.mongodb import add_review; print(add_review(1, 's300', 'so tense, could not look away', spoiler=False, tags=['scary']))"
```

`True` means it was saved. `False` means that user already reviewed that movie. An error message means the user ID or movie ID doesn't exist, or the text is empty.

**Option B. Where:** MongoDB Compass → `netflix_review_db` → `reviews` → **ADD DATA** → **Insert document**, then paste:

```json
{
  "user_id": 1,
  "movie_id": "s300",
  "review_text": "so tense, could not look away",
  "spoiler": false,
  "tags": ["scary"],
  "created_at": {"$date": "2026-11-11T02:00:00Z"}
}
```

Compass still enforces the collection rules (types, no empty text, one review per user per movie), but it **skips** the check that the user and movie exist in MariaDB. So Option A is safer.

To add a review to the sample dataset itself, add a row to `data/reviews.csv` and rerun `python -m scripts.convert_reviews_to_mongo`.

**Stuck?** `ServerSelectionTimeoutError` usually means MongoDB isn't running (Windows **Services** app → MongoDB Server → Start). `No module named 'db'` means Command Prompt isn't in the project folder; run the `cd` line again.

For how to use the review functions in the app, with copy-paste examples, see [`docs/mongodb_handover.md`](docs/mongodb_handover.md). The full function reference is in [`docs/reviews_api.md`](docs/reviews_api.md).

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

MongoDB is used for review documents (`reviews` collection). The document model is described in `docs/mongodb_model.md`; setup, function contracts and sample calls are in `docs/mongodb_handover.md`.

## Development Status

- **Catalogue foundation:** Implemented and tested.
- **Ratings and watchlist:** Implemented and tested.
- **MongoDB reviews:** Implemented and tested.
- **Streamlit interface:** Under development.

## Team Integration

The catalogue module uses `movie_id` as the unique movie identifier. Other modules should use the same ID when associating ratings, watchlist entries and MongoDB reviews with catalogue movies.

Each developer must initialise their own local database. The GitHub repository contains the schema and import scripts, not the populated MariaDB database itself.