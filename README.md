# CineVault

**INF2003 Database Systems Group 44 Project**

CineVault is a movie discovery and community-review application developed using **Streamlit, MariaDB and MongoDB**. Members can explore movies, browse community ratings and reviews, submit their own ratings and reviews, manage their watchlist, and track their watched history.

## 1. Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Programming Language | Python |
| Relational Database | MariaDB |
| NoSQL Database | MongoDB |
| Database Connectivity | PyMySQL, PyMongo |
| Data Processing | pandas |
| Password Hashing | Argon2id |

## 2. Application Features

| Page | Features |
|---|---|
| **Home** | Explore featured movies, highest-rated movies, most-reviewed movies and popular community content. |
| **Search** | Search movies, actors and genres using universal search, filters, Any/All matching, sorting and incremental loading. |
| **Movie Details** | View movie information, community ratings and reviews. Submit ratings, write reviews and manage the watchlist. |
| **My Activity** | View personal ratings, reviews, watched history and watchlist in one place. |

### Database Integration

CineVault uses both databases for different purposes:

- **MariaDB:** Stores user accounts, movie catalogue information, genres, actors, numerical ratings, watchlists and watched history.
- **MongoDB:** Stores written community reviews, including review text, tags, spoiler status and timestamps. It also contains a denormalised movie catalogue collection with embedded genres and actors for selected queries.

The Streamlit application integrates information from both databases through Python. For example, written reviews are retrieved from MongoDB and combined with their authors' corresponding star ratings from MariaDB before being displayed.

## 3. Project Structure

```text
cinevault-app/
│
├── .streamlit/                 # Streamlit configuration
├── data/                       # Movie and review datasets
├── db/                         # MariaDB and MongoDB operations
├── docs/
│   ├── api/                    # Database API documentation
│   ├── database/               # ER diagrams
│   ├── testing/                # Testing documentation and results
│   ├── mongodb_handover.md
│   ├── mongodb_model.md
│   ├── review_dataset_notes.md
│   └── streamlit_implementation.md
│
├── notebooks/                  # Jupyter notebooks
│
├── performance/
│   ├── results/                # Backend benchmark CSV files
│   ├── screenshots/
│   │   ├── browser_traces/     # Chrome Performance captures
│   │   └── network/            # Chrome Network captures
│   └── performance_analysis.md
│
├── screens/                    # Streamlit application pages
├── scripts/                    # Import, conversion and seeding scripts
├── sql/                        # SQL schemas and queries
├── tests/                      # Automated test modules
├── ui/                         # Reusable UI components and styling
│
├── app.py                      # Streamlit application entry point
├── .env.example                # Example environment configuration
├── .gitignore
├── README.md
└── requirements.txt            # Python dependencies
```

## 4. Prerequisites

Install the following before setting up CineVault:

- Git
- Python 3.14.6 (used for the latest local testing)
- MariaDB Server
- MongoDB Community Server
- Visual Studio Code
- HeidiSQL or another MariaDB client

Keep both MariaDB and MongoDB services running while using the application.

## 5. Installation and Setup (Windows)

Follow these steps in order. Run the commands in the VS Code PowerShell terminal from the project root directory.

### Step 1: Clone the repository

```powershell
git clone https://github.com/tsuki5281/cinevault-app.git
cd cinevault-app
```

### Step 2: Create a Python virtual environment

Check the installed Python versions:

```powershell
py --list
```

Create a virtual environment using Python 3.14:

```powershell
py -3.14 -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This temporarily allows script execution in the current PowerShell session.

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 3: Configure environment variables

Copy the example configuration file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter your own MariaDB credentials.

The configuration should contain:

```dotenv
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=netflix_review_db

MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=netflix_review_db
```

Replace the MariaDB username and password with your own local credentials.

**Important:** Never commit `.env` to GitHub. It contains local database credentials and is excluded through `.gitignore`. Only `.env.example` should be shared.

### Step 4: Create the MariaDB database and tables

1. Open HeidiSQL and connect to the local MariaDB server.
2. Create the database:

```sql
CREATE DATABASE netflix_review_db;
```

3. Select `netflix_review_db`.
4. Execute the following SQL files individually in this order:

| Order | SQL File | Purpose |
|---|---|---|
| 1 | `sql/schema.sql` | Creates the core relational tables for users, movies, genres, actors, ratings and watchlists. |
| 2 | `sql/authentication.sql` | Creates the `user_credentials` table for account authentication. |
| 3 | `sql/watched_movies.sql` | Creates the `watched_movies` table. |

Verify the tables:

```sql
SHOW TABLES;
```

You should see 10 tables:

`actors`, `genres`, `movie_actors`, `movie_genres`, `movies`, `ratings`, `user_credentials`, `users`, `watched_movies` and `watchlist`.

### Step 5: Import the datasets

Run the following scripts from the project root.

**A. Import the movie catalogue into MariaDB**

```powershell
python -m scripts.import_movies
```

The cleaned dataset `data/netflix_movies_cleaned.csv` is used for the import.

Expected output:

```text
Dataset loaded successfully: 4677 movies
Movie catalogue imported successfully!
```

**B. Initialise MongoDB**

```powershell
python -m scripts.init_mongodb
```

This creates the reviews collection, validation rules and required indexes. By default, existing reviews are preserved.

Expected output includes:

```text
Collection 'reviews' ready with validation rules
Indexes: _id_, uniq_user_movie, movie_newest
```

**C. Import the sample reviews**

```powershell
python -m scripts.convert_reviews_to_mongo
```

This converts `data/reviews.csv` into MongoDB review documents. It also creates or retrieves the corresponding sample users in MariaDB and synchronises imported reviews with watched history.

**Important:** This script replaces previously imported sample-user reviews. Reviews from other users are preserved. Run it during initial setup or when intentionally rebuilding the sample review dataset.

**D. Copy the movie catalogue into MongoDB**

```powershell
python -m scripts.convert_movies_to_mongo
```

This creates the MongoDB `movies` collection with embedded genre and actor arrays.

**Important:** This script rebuilds the MongoDB `movies` collection. Run it during initial setup or when intentionally refreshing the denormalised movie catalogue.

### Step 6: Add demonstration ratings and activity

The following scripts are optional. They populate the prepared demo profiles with sample ratings, watched history and watchlist entries.

```powershell
python -m scripts.seed_demo_ratings
python -m scripts.seed_demo_activity
```

These scripts preserve existing ratings and activity entries rather than creating duplicates.

The prepared demo profiles are:

- `sample_user_06`
- `sample_user_07`
- `sample_user_11`

These are demonstration accounts with sample activity, not real user records.

## 6. Running CineVault

Whenever you want to launch the application:

1. Start the MariaDB and MongoDB services.
2. Open the project folder in VS Code.
3. Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Start Streamlit:

```powershell
python -m streamlit run app.py
```

5. Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

### Important: Dark Mode

CineVault is designed for **Dark Mode only**. Light Mode and Automatic Mode are not supported and may affect the appearance of text, cards and other interface elements.

In Streamlit, select:

**⋮ → Settings → Theme → Dark**

## 7. User Authentication

CineVault provides two ways to access the application:

- **Demo Profile:** Select one of the prepared demo accounts from the login screen. No password is required.
- **Create Account:** Register with a username and password, then sign in using the registered credentials.

Official account passwords are stored as Argon2id hashes in MariaDB.

## 8. Testing

The project includes automated tests, functional checks and database integration tests.

### Automated Testing

Test modules are located in the `tests/` directory. They cover:

- Account authentication and registration.
- Movie catalogue retrieval and filtering.
- Homepage data and recommendations.
- Ratings and rating distributions.
- Search suggestions and sorting.
- Review management and sorting.
- Watched history and member activity.
- Cross-database integration.

Run the test suite from the project root with the virtual environment activated and both database services running:

```powershell
python -m unittest discover -s tests -v
```

### Testing Documentation

Refer to `docs/testing/` for the test results and testing approach.

## 9. Performance Evaluation

Performance testing was conducted locally on 27 November 2026 using the updated CineVault implementation.

The evaluation includes:

- Sequential database benchmarks.
- Concurrent database benchmarks using 1, 5 and 10 worker threads.
- MongoDB review-index performance comparison.
- MariaDB versus MongoDB genre-search comparison.
- Chrome DevTools Network profiling.
- Chrome DevTools Performance profiling.

The benchmark results are stored in:

| File | Description |
|---|---|
| `performance/results/sequential_results.csv` | Sequential database benchmark results. |
| `performance/results/concurrency_results.csv` | Concurrent database benchmark results. |
| `performance/performance_analysis.md` | Performance methodology, results, observations and limitations. |

Supporting screenshots from the browser profiling tests are available in:

- `performance/screenshots/network/`
- `performance/screenshots/browser_traces/`

### Reproducing the Backend Benchmarks

Run the main database benchmark:

```powershell
python scripts\benchmark_performance.py
```

Run the MongoDB-specific performance tests:

```powershell
python -m scripts.performance_mongodb
```

The main benchmark is read-only and saves its output in `performance/results/`.

## 10. Project Documentation

Additional technical documentation is organised by topic.

| Folder / File | Contents |
|---|---|
| `docs/api/` | Catalogue, ratings, watchlist and reviews API documentation. |
| `docs/database/` | MariaDB ER diagram in PNG and editable Draw.io formats. |
| `docs/testing/` | SQL, catalogue, MongoDB and Streamlit testing results. |
| `docs/mongodb_handover.md` | MongoDB implementation handover notes. |
| `docs/mongodb_model.md` | MongoDB collections, document structure and design decisions. |
| `docs/review_dataset_notes.md` | Sample review dataset generation and design notes. |
| `docs/streamlit_implementation.md` | Streamlit application structure, screens and database integration. |
| `notebooks/` | Dataset inspection notebook. |
| `performance/` | Performance analysis, benchmark results and supporting screenshots. |

## 11. Troubleshooting

| Problem | Suggested check |
|---|---|
| Python is not recognised | Check installed Python versions using `py --list` and activate `.venv`. |
| PowerShell blocks virtual environment activation | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. |
| Missing Python module | Activate `.venv` and run `python -m pip install -r requirements.txt`. |
| MariaDB connection error | Check the MariaDB service and the database credentials in `.env`. |
| MongoDB connection timeout | Check that MongoDB Server is running and that `MONGO_URI` is correct. |
| Missing database tables | Verify that the SQL files in Step 4 were executed in the correct order. |
| Missing demo profiles | Check that the movie import and sample review conversion completed successfully. |
| Missing movie or review data | Verify that the relevant import and conversion scripts completed successfully. |
| Incorrect application colours or text | Change the Streamlit theme to Dark Mode. |

## 12. Notes

- The movie catalogue and sample review datasets are provided in the `data/` directory.
- The sample review dataset is used for demonstration and testing.
- MariaDB and MongoDB are separate database systems with distinct responsibilities.
- The application integrates information from both databases through its Python application layer.
- Performance measurements represent local testing conditions and should not be interpreted as production-scale performance guarantees.