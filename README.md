# CineVault

**INF2003 Database Systems Group Project**

CineVault is a Netflix-inspired movie discovery and review application built with Streamlit, MariaDB and MongoDB. Users can explore a movie catalogue, discover community favourites, rate and review movies, maintain a watchlist, and keep track of their watched history.

## Features

- **User accounts:** Register an official account, sign in, or explore the application using a prepared demo profile.
- **Home and discovery:** Explore a featured movie, highest-rated movies, most-reviewed movies and movies by genre.
- **Movie search:** Search by movie title and use suggestions, genre filters and actor filters. Multiple filters support Any/All matching.
- **Catalogue sorting:** Browse movie results with sorting and pagination, including community-rating-based sorting.
- **Movie details:** View movie descriptions, directors, cast, country, genres, ratings and community reviews.
- **Community ratings:** Submit and update 1–5 star ratings and view community rating summaries and distributions.
- **Community reviews:** Write, edit and delete reviews, add tags, mark spoilers, and browse reviews using different sorting options.
- **My Activity:** View personal ratings and reviews, watched history and saved watchlist movies.

## Technology Stack

- **Frontend:** Streamlit
- **Relational database:** MariaDB
- **Document database:** MongoDB
- **Language:** Python
- **Database libraries:** PyMySQL and PyMongo
- **Other libraries:** pandas, python-dotenv and argon2-cffi

## Repository Structure

```text
netflix-review-app/
├── app.py                         # Streamlit application entry point
├── .env.example                   # Environment-variable template
├── requirements.txt               # Python dependencies
├── data/
│   ├── netflix_movies_cleaned.csv # Cleaned movie catalogue imported into MariaDB
│   ├── reviews.csv                # Sample community review dataset
│   └── ...                        # Other source and supporting datasets
├── db/
│   ├── authentication.py          # Account registration and login
│   ├── activity.py                # User activity data operations
│   ├── catalogue.py               # Movie catalogue queries
│   ├── home.py                    # Data retrieval for the Home page
│   ├── mariadb.py                 # MariaDB ratings, watchlist and watched history
│   └── mongodb.py                 # MongoDB review and document operations
├── screens/
│   ├── login.py                   # Sign-in, registration and demo profiles
│   ├── home.py                    # Home and movie discovery screen
│   ├── search.py                  # Movie search and catalogue screen
│   ├── movie_details.py            # Movie details, ratings and reviews
│   └── activity.py                # My Activity screen
├── ui/
│   ├── components.py              # Shared interface components
│   ├── review_card.py             # Community review display component
│   └── styles.py                  # Application styling
├── scripts/
│   ├── import_movies.py           # Imports the cleaned movie catalogue into MariaDB
│   ├── init_mongodb.py             # Initialises the MongoDB reviews collection
│   ├── convert_reviews_to_mongo.py # Imports sample reviews and creates sample users
│   ├── convert_movies_to_mongo.py  # Copies movie documents into MongoDB
│   ├── create_official_account.py  # Optional command-line account creation
│   ├── seed_demo_ratings.py        # Adds illustrative demo ratings
│   ├── seed_demo_activity.py       # Adds sample watched-history and watchlist entries
│   └── ...                        # Other data preparation and performance scripts
├── sql/
│   ├── schema.sql                 # Core relational database tables
│   ├── authentication.sql         # Official-account credential table
│   ├── watched_movies.sql        # Watched-history table
│   └── ...                        # Validation and advanced SQL scripts
├── tests/                         # Automated test files
├── docs/                          # API, implementation, testing and database documentation
└── performance_results/           # Backend benchmark result CSV files
```

## Installation and Setup

The following steps describe a first-time local setup. Each team member must configure their own MariaDB and MongoDB instances. The repository contains the schema, data files and scripts, but does not contain a copy of another team member's local database.

### 1. Prerequisites

Install the following before starting:

- Git
- Python
- MariaDB Server
- MongoDB Community Server
- A code editor such as Visual Studio Code
- A MariaDB client such as HeidiSQL (recommended for running the SQL scripts)

Make sure both the MariaDB and MongoDB services are running before launching the application.

### 2. Clone the repository

Clone the repository and open the project root folder in VS Code:

```powershell
git clone https://github.com/tsuki5281/netflix-review-app.git
cd netflix-review-app
```

To use the latest Streamlit integration branch before it is merged into `main`, switch to the project branch:

```powershell
git switch nusrat/cinevault-streamlit
```

### 3. Create a Python virtual environment and install dependencies

From the project root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies listed in `requirements.txt`:

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file by copying `.env.example`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter the connection details for your own local databases:

```dotenv
# MariaDB
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=netflix_review_db

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=netflix_review_db
```

Replace the MariaDB username and password with your own database credentials. Update the MongoDB URI if your local MongoDB instance uses a different connection string.

**Important:** Do not commit or share your `.env` file. It contains local credentials and is excluded through `.gitignore`.

## Database Setup

### 5. Create and initialise the MariaDB database

Start MariaDB and create a database named `netflix_review_db` using HeidiSQL or another MariaDB client:

```sql
CREATE DATABASE netflix_review_db;
```

Select the newly created database, then execute the following SQL scripts **in this exact order**:

| Order | SQL script | Purpose |
|---:|---|---|
| 1 | `sql/schema.sql` | Creates the eight core tables, including `users`, `movies`, `ratings` and `watchlist`. |
| 2 | `sql/authentication.sql` | Creates `user_credentials`, which stores the password hash for each official account and references `users`. |
| 3 | `sql/watched_movies.sql` | Creates `watched_movies`, which stores each user's watched-history entries. |

The second script must run after `schema.sql` because `user_credentials.user_id` references `users.user_id`. The watched-history script also references the existing `users` and `movies` tables.

After executing all three scripts, the database has the eight core tables plus the two additional tables for authentication and watched history.

### 6. Import the movie catalogue into MariaDB

The cleaned dataset is located at `data/netflix_movies_cleaned.csv`. From the project root, run:

```powershell
python -m scripts.import_movies
```

The script imports the movie records and their genre and actor associations into MariaDB. The cleaned catalogue contains 4,677 movie records.

### 7. Initialise MongoDB and import the review and movie documents

Ensure MongoDB Server is running and that the `MONGO_URI` and `MONGO_DB_NAME` values in `.env` are correct.

From the repository root, run these commands in order:

```powershell
python -m scripts.init_mongodb
python -m scripts.convert_reviews_to_mongo
python -m scripts.convert_movies_to_mongo
```

These scripts:

1. Create or initialise the MongoDB `reviews` collection, including its validation rules and indexes.
2. Convert the supplied `data/reviews.csv` records into MongoDB review documents. The conversion also creates the corresponding `sample_user_...` accounts in MariaDB when they do not already exist. These sample users make the prepared demo profiles available on the login screen.
3. Copy the movie catalogue from MariaDB into MongoDB's `movies` collection for review-related queries.

Run the commands from the repository root using `python -m ...` so that the project modules can be imported correctly.

### 8. (Recommended) Load the prepared demo activity and ratings

The project includes optional scripts that add sample activity to the prepared demo profiles. Run them after the MariaDB and MongoDB imports above:

```powershell
python -m scripts.seed_demo_ratings
python -m scripts.seed_demo_activity
```

- `seed_demo_ratings.py` adds illustrative coursework ratings for selected sample users and movies. It only adds missing entries and preserves existing ratings. These are demo values, not genuine audience ratings.
- `seed_demo_activity.py` adds watched-history and watchlist entries for the `sample_user_07` demo profile. It is useful for exploring the My Activity screen.

These steps are recommended when setting up CineVault for a project demonstration. They are not required to create a new official account.

## Running CineVault

### 9. Launch the Streamlit application

Check that MariaDB and MongoDB are running, activate the Python virtual environment, and execute this command from the project root:

```powershell
streamlit run app.py
```

Streamlit will display a local URL in the terminal and usually open the application in your browser.

### 10. Sign in or create an account

The login screen provides two ways to access CineVault:

- **Create Account:** Register a new official account using a username and password. Passwords are hashed using Argon2id before being stored in MariaDB.
- **Demo Profile:** Select one of the prepared profiles to explore the application with sample ratings, reviews and activity. Demo profiles are available after the sample review conversion has been completed.

The available demo profiles are:

| Profile | Username | Description |
|---|---|---|
| Active Member | `sample_user_06` | A member with ratings and written reviews. |
| Reviewer | `sample_user_11` | A review-focused member with an extensive review history. |
| Movie Explorer | `sample_user_07` | A profile for exploring watched movies, saved titles and community reviews. |

An official account can also be created from the terminal using the optional helper script:

```powershell
python -m scripts.create_official_account
```

### Application Testing (Very Important!!!)
– Step-by-step guide for manually testing CineVault's features and recording feedback.
- [Application Testing Checklist](application_test_checklist.md) 

## Testing

Automated tests are located in `tests/`. The selected Streamlit-related test coverage includes authentication, homepage data, genres, actor recommendations, search suggestions, movie-card details, rating distribution and sorting, watched history, user activity and review sorting.

For the selected test files, test commands, functional testing, database integration checks and testing limitations, see [`docs/streamlit_testing.md`](docs/streamlit_testing.md).

The project also contains separate database test documentation:

- [`docs/catalogue_test_results.md`](docs/catalogue_test_results.md)
- [`docs/sql_test_results.md`](docs/sql_test_results.md)
- [`docs/mongodb_test_results.md`](docs/mongodb_test_results.md)

## Database Design

CineVault uses both relational and document-oriented storage:

- **MariaDB** stores the structured movie catalogue, genres, actors, user accounts, credentials, ratings, watchlists and watched history.
- **MongoDB** stores community review documents and a movie-document collection used by review-related queries.

The movie identifier (`movie_id`) is used to associate a movie across the application and its databases. The MariaDB ER diagram is available in [`docs/er_diagram.png`](docs/er_diagram.png), with an editable version in [`docs/er_diagram.drawio`](docs/er_diagram.drawio).

## Documentation

| Document | Description |
|---|---|
| [`docs/streamlit_implementation.md`](docs/streamlit_implementation.md) | Overview of the Streamlit application, its screens, user interactions and database integration. |
| [`docs/streamlit_testing.md`](docs/streamlit_testing.md) | Automated, functional, integration and regression testing for the Streamlit application. |
| [`docs/performance_analysis.md`](docs/performance_analysis.md) | Backend benchmark results and frontend performance observations. |
| [`docs/catalogue_api.md`](docs/catalogue_api.md) | Catalogue functions, parameters and return values. |
| [`docs/ratings_watchlist_api.md`](docs/ratings_watchlist_api.md) | Rating, watchlist, watched-history and rating-helper functions. |
| [`docs/reviews_api.md`](docs/reviews_api.md) | MongoDB review functions and their Streamlit integration. |
| [`docs/mongodb_model.md`](docs/mongodb_model.md) | MongoDB document model and collection design. |
| [`docs/mongodb_handover.md`](docs/mongodb_handover.md) | MongoDB setup, review import and usage guidance. |
| [`docs/er_diagram.png`](docs/er_diagram.png) | MariaDB entity-relationship diagram. |

## Troubleshooting

| Problem | What to check |
|---|---|
| MariaDB connection error | Confirm the MariaDB service is running and that `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` and `DB_NAME` in `.env` are correct. |
| MongoDB `ServerSelectionTimeoutError` | Confirm the MongoDB service is running and that `MONGO_URI` points to the correct instance. |
| `Table '...user_credentials' doesn't exist` | Execute `sql/authentication.sql` after `sql/schema.sql` in the `netflix_review_db` database. |
| `Table '...watched_movies' doesn't exist` | Execute `sql/watched_movies.sql` after the core schema has been created. |
| `ModuleNotFoundError: No module named 'db'` | Open a terminal at the repository root and run project scripts using `python -m scripts.<script_name>`. |
| Demo profiles are not displayed | Run `python -m scripts.convert_reviews_to_mongo` after importing the MariaDB movie catalogue. This creates the sample users in MariaDB. |
| Home page or review data is empty | Check that the movie and review imports completed, then run the optional demo seeding scripts if sample ratings and activity are needed. |

For database-specific setup details, refer to the MongoDB handover and API documentation linked above.
