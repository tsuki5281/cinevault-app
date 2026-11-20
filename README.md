# CineVault

**INF2003 Database Systems Group Project**

CineVault is a Netflix-inspired movie discovery and community-review application built with **Streamlit, MariaDB and MongoDB**. Members can explore movies, browse community ratings and reviews, rate and review titles, manage a watchlist, and view their watched history.

## Important: use Dark Mode

> **CineVault is designed for DARK MODE ONLY.** The colours, text, cards and page styling were designed for a dark interface. Light Mode and Automatic Mode are not supported and may cause parts of the interface to look incorrect or become difficult to read.
>
> When the app opens, select **⋮ (top-right menu) → Settings → Theme → Dark**. Keep the app in Dark Mode while using and testing CineVault.

## What you need

Install these before starting:

- Git
- Python 3.13
- MariaDB Server
- MongoDB Community Server
- Visual Studio Code
- HeidiSQL or another MariaDB client

Keep the MariaDB and MongoDB services running while using the application.

## First-time setup (Windows)

Follow the steps below **in order**. Run the commands in the VS Code PowerShell terminal, from the project folder unless stated otherwise.

### 1. Download the project

Clone the Streamlit integration branch:

```powershell
git clone https://github.com/tsuki5281/cinevault-app.git
cd cinevault-app
```

You should now be in the folder that contains `app.py`, `requirements.txt`, `db/`, `screens/` and `scripts/`.

### 2. Set up Python

Create and activate a virtual environment, then install the project packages and Streamlit:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt 
```

**What success looks like:**

- The terminal prompt starts with `(.venv)` after activation.
- Package installation finishes with a message similar to:

```text
Successfully installed ... streamlit ... pandas ... PyMySQL ... pymongo ...
```

If PowerShell blocks the activation script, run this once in the same terminal, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Create your local database settings

Copy the example environment file and open the new `.env` file:

```powershell
Copy-Item .env.example .env
notepad .env
```

Enter your own MariaDB username and password. Keep the database name and MongoDB settings as shown unless your local setup is different:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=netflix_review_db

MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=netflix_review_db
```

Save and close the file. **Never commit `.env` to GitHub** because it contains your local database credentials. The `.env` file is ignored by Git.

### 4. Create the MariaDB database and tables

1. Open HeidiSQL and connect to your local MariaDB server.
2. Run this query to create the database:

```sql
CREATE DATABASE netflix_review_db;
```

3. Select `netflix_review_db` in HeidiSQL.
4. Open and execute these three files **one at a time, in this order**:

| Order | File | What it creates |
|---:|---|---|
| 1 | `sql/schema.sql` | The eight core tables for users, movies, genres, actors, ratings and watchlists. |
| 2 | `sql/authentication.sql` | The `user_credentials` table for official-account password hashes. |
| 3 | `sql/watched_movies.sql` | The `watched_movies` table for member viewing history. |

**Check that the tables were created:** run:

```sql
SHOW TABLES;
```

You should see **10 tables**: `actors`, `genres`, `movie_actors`, `movie_genres`, `movies`, `ratings`, `user_credentials`, `users`, `watched_movies` and `watchlist`.

### 5. Import the movie and review data

Run each command below from the project root. Wait for the success message before moving to the next command.

**A. Import the movie catalogue into MariaDB**

```powershell
python -m scripts.import_movies
```

Expected output:

```text
Dataset loaded successfully: 4677 movies
Movie catalogue imported successfully!
```

**B. Initialise MongoDB**

```powershell
python -m scripts.init_mongodb
```

Expected output:

```text
MongoDB database: netflix_review_db
Collection 'reviews' ready with validation rules
Indexes: _id_, uniq_user_movie, movie_newest
```

**C. Import the sample reviews**

```powershell
python -m scripts.convert_reviews_to_mongo
```

Expected output will include:

```text
Read 144 rows from data/reviews.csv
Added ... imported reviews to watched history
Converted and inserted: ... reviews | Skipped: ...
Review dataset converted successfully!
```

The numbers may vary if the CSV contains invalid rows or the script has already been run. This script creates the sample demo users in MariaDB and imports their reviews into MongoDB. It also adds the imported review movies to `watched_movies`, so sample review activity is reflected in Watched History. The importer can be rerun without creating duplicate watched-history entries.

**D. Copy the movie documents into MongoDB**

```powershell
python -m scripts.convert_movies_to_mongo
```

Expected output:

```text
Read from MariaDB: 4677 movies, ... movie-genre links, ... movie-actor links
Written to MongoDB 'movies' collection: 4677 documents
Example document:
{ ... }
Conversion completed successfully!
```

The movie-genre and movie-actor link counts and example document will depend on the imported catalogue. The important checks are **4,677 documents written** and `Conversion completed successfully!`.

### 6. Add the demo ratings and activity

Run these optional scripts to give the prepared demo profiles sample ratings, watched history and watchlist entries:

```powershell
python -m scripts.seed_demo_ratings
python -m scripts.seed_demo_activity
```

For the ratings script, a fresh database should show output similar to:

```text
Demo rating seed completed!
New ratings inserted: 19
Existing ratings preserved: 0
Total demo rating assignments: 19
```

The numbers change when the script is rerun. Existing ratings are preserved. The activity script also skips records that already exist. On completion, it reports how many watched-history and watchlist entries were newly added; entries already in the database are left unchanged. The final message should confirm that demo activity setup is complete.

Example final message:

```text
Demo activity setup complete.
```

The featured activity profiles are:

| Demo profile | Watched movies | Watchlist movies |
|---|---:|---:|
| `sample_user_06` | 4 | 2 |
| `sample_user_07` | 3 | 3 |
| `sample_user_11` | 3 | 4 |

These are prepared demonstration records, not real user activity.

## Run CineVault

Whenever you want to use the app:

1. Start the MariaDB and MongoDB services.
2. Open the `netflix-review-app` folder in VS Code.
3. Open a terminal in the project root and activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Launch Streamlit:

```powershell
streamlit run app.py
```

Expected output includes a local address similar to:

```text
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Open the local URL in your browser. **Set the theme to Dark Mode** using **⋮ → Settings → Theme → Dark** before exploring the application.

## Sign in

You can access CineVault in either of these ways:

- **Demo Profile:** choose a prepared demo account on the login screen. Demo profiles are available after the sample review import has completed.
- **Create Account:** register a new account with a username and password. Passwords are stored as Argon2id hashes in MariaDB.

The featured demo usernames are `sample_user_06`, `sample_user_07` and `sample_user_11`. Select them from the Demo Profile area on the login screen; no password is required for demo access.

## Main features

| Page | What you can do |
|---|---|
| **Home** | Explore featured movies and community highlights. |
| **Search** | Search by title, actor or genre, apply filters and sort results. |
| **Movie Details** | View movie information, submit ratings and reviews, and update your watchlist. |
| **My Activity** | View and manage your ratings, reviews, watched history and watchlist. |

## Testing and documentation

- [Application Testing Checklist](docs/application_test_checklist.md): manual steps for checking the main app features and recording issues.
- [Streamlit Implementation](docs/streamlit_implementation.md): application screens, interactions and database integration.
- [Streamlit Testing](docs/streamlit_testing.md): automated tests and testing approach.
- [Catalogue API](docs/catalogue_api.md): movie catalogue functions.
- [Ratings and Watchlist API](docs/ratings_watchlist_api.md): ratings, watchlist and watched-history functions.
- [Reviews API](docs/reviews_api.md): MongoDB review functions.
- [MongoDB Model](docs/mongodb_model.md): document and collection design.
- [MariaDB ER Diagram](docs/er_diagram.png): relational database design.

## Troubleshooting

| Problem | Check this first |
|---|---|
| `python` is not recognised | Activate `.venv` first. If Python is still not found, close and reopen the terminal and check that Python 3.13 is installed. Use `py -3.13` for the virtual-environment creation command. |
| PowerShell will not activate `.venv` | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current terminal, then activate again. |
| MariaDB connection error | Check the MariaDB service and the `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` and `DB_NAME` values in `.env`. |
| MongoDB connection timeout | Check that MongoDB Server is running and `MONGO_URI` in `.env` is correct. |
| A table does not exist | Re-run the SQL files in Step 4 in the stated order, using the `netflix_review_db` database. |
| Demo profiles are missing | Run `python -m scripts.convert_reviews_to_mongo` after importing the movie catalogue. |
| Movie or review data is missing | Check that all four imports in Step 5 completed successfully, then run the demo seeding commands in Step 6. |
| App colours or text look wrong | Change Streamlit's theme to **Dark**. CineVault's design does not support Light or Automatic Mode. |

## Technology stack

- **Frontend:** Streamlit
- **Relational database:** MariaDB
- **Document database:** MongoDB
- **Language:** Python
- **Libraries:** pandas, PyMySQL, PyMongo, python-dotenv and argon2-cffi
