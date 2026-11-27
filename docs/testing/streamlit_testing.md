# CineVault Streamlit Testing

## 1. Testing Overview

Testing was carried out to check that the CineVault application features behave as expected, that the Streamlit interface can work with the existing database modules, and that the relevant functions continue to behave correctly after integration updates.

The testing activities covered three areas:

- **Automated testing:** Python test modules were used to check individual functions, validation rules, returned data and selected cross-database integration behaviour.
- **Functional testing:** The Streamlit application was used to check the main user-facing workflows, including authentication, movie discovery, movie details, community reviews and My Activity.
- **Integration and regression testing:** Relevant workflows were checked across MariaDB and MongoDB, with particular attention to features that combine information from both databases and to existing sorting and pagination behaviour.

This document focuses on the 12 test files selected for the Streamlit integration work. The separate catalogue, ratings/watchlist and general review test files are not repeated here because their test information is maintained with the corresponding API documentation.

## 2. Testing Environment

Testing was performed in the local CineVault development environment. The automated tests use Python's `unittest` framework and connect to the configured MariaDB and MongoDB databases where database records are required.

The test modules cover both data retrieval and operations that create, update or remove records. Tests that require database records use test-specific users, movies or review documents. The relevant test setup and cleanup routines are used to remove temporary records where provided.

The Streamlit application was also run locally to check the user-facing workflows. Performance measurements and benchmarking are documented separately in `performance_analysis.md` and are outside the scope of this document.

## 3. Automated Testing

A total of **12 automated test files**, containing **70 test methods**, were included in this testing scope. All 12 test files were executed successfully in the local development environment.

### 3.1 Automated Test Coverage

| No. | Test file | Test methods | Coverage |
|---:|---|---:|---|
| 1 | `test_authentication.py` | 9 | Account creation, successful and unsuccessful login, empty credentials, duplicate usernames, invalid registration inputs, password hashing and demo-account retrieval. |
| 2 | `test_genres.py` | 4 | Genre retrieval, required fields, alphabetical ordering and uniqueness. |
| 3 | `test_homepage.py` | 4 | Homepage data sections, featured movie consistency with the highest-rated result, configurable result limits and invalid limit handling. |
| 4 | `test_movie_card_details.py` | 7 | Movie information returned for cards, genre information, duplicate and unknown IDs, empty input, invalid input and input-size limits. |
| 5 | `test_rating_distribution.py` | 1 | Retrieval and structure of a movie's rating distribution. |
| 6 | `test_rating_sorting.py` | 9 | Batch rating summaries, user-specific ratings, empty inputs, highest-rated ordering, rating-based pagination and sorting validation. It also checks that the catalogue can return all filtered matches for global rating ranking. |
| 7 | `test_recommended_actors.py` | 8 | Number and structure of actor recommendations, uniqueness, ranking by movie count, association with the selected demo movies, custom limits and invalid limits. |
| 8 | `test_review_sorting.py` | 6 | Separation of MongoDB review retrieval from rating data, highest-rated review ordering, rating enrichment, pagination, newest/oldest ordering and invalid sort options. |
| 9 | `test_search_suggestions.py` | 6 | Suggestions across movies, actors and genres, prefix-match ordering, result limits, empty keywords, unmatched keywords and invalid limits. |
| 10 | `test_watched_movies.py` | 6 | Adding and retrieving watched movies, duplicate entries, removing watched status, missing records, invalid IDs and user-specific history. |
| 11 | `test_activity.py` | 7 | Combining rating and review activity, rating-only and review-only movies, duplicate movie handling, latest-activity ordering, review pagination and invalid user IDs. |
| 12 | `test_activity_summary.py` | 3 | Activity counts for ratings, reviews, watched movies and watchlist items, zero activity for a new user and invalid user IDs. |
|  | **Total** | **70** | **12 test files** |

### 3.2 Running the Selected Test Files

Run the following command from the repository root to execute the 12 selected test modules using `unittest`:

```bash
python -m unittest \
  tests.test_authentication \
  tests.test_genres \
  tests.test_homepage \
  tests.test_movie_card_details \
  tests.test_rating_distribution \
  tests.test_rating_sorting \
  tests.test_recommended_actors \
  tests.test_review_sorting \
  tests.test_search_suggestions \
  tests.test_watched_movies \
  tests.test_activity \
  tests.test_activity_summary -v
```

The tests require the database services and connection settings used by the local CineVault development environment to be available.

## 4. Functional Testing

Functional testing was used to check the main CineVault workflows from the perspective of a member using the Streamlit interface. The following areas were checked:

| Application area | Functional checks |
|---|---|
| **Authentication** | Creating an account, signing in with valid credentials, handling invalid credentials, accessing demo profiles and signing out. |
| **Home** | Loading the homepage sections, displaying featured and recommended movie content, and opening a selected movie. |
| **Search and catalogue** | Entering search keywords, selecting movie/actor/genre suggestions, applying genre and actor filters, using Any/All matching, changing sorting options and loading additional results. |
| **Movie cards** | Displaying movie titles, genres and community rating information, including the state where a movie has not yet received ratings. |
| **Movie Details** | Opening a selected movie, viewing its information and rating summary, submitting or updating a rating, and managing its watchlist status. |
| **Community Reviews** | Submitting, editing and deleting reviews; applying spoiler visibility and review tags; and changing review sorting options. |
| **My Activity** | Viewing the signed-in member's ratings, reviews, watchlist and watched history, and using the available management actions. |

The functional checks confirmed that the main user workflows could be carried out through the running application. The automated test modules provide additional checks for the underlying functions and data behaviour used by these screens.

## 5. Database Integration Testing

Integration testing focused on how the Streamlit application uses the existing MariaDB and MongoDB modules and how information from both databases is combined when required.

### 5.1 MariaDB Integration

The selected tests exercise MariaDB-backed features including:

- Account creation and authentication, including password-hash storage.
- Genre retrieval and movie information used by the homepage and movie cards.
- Rating distribution, batch rating summaries and user-specific movie ratings.
- Rating-based movie ranking and pagination.
- Watched-history operations and member activity summaries.
- Combining a member's ratings and reviews into a consolidated activity list.

### 5.2 MongoDB and Cross-Database Review Integration

Community review documents are stored and retrieved through MongoDB, while member star ratings are stored in MariaDB. The review integration tests check that these responsibilities remain separate and that the application combines the information for display.

In particular, `test_review_sorting.py` checks that:

- MongoDB review retrieval returns review documents without a `rating_stars` field.
- The application-level review integration attaches the corresponding MariaDB rating when one exists.
- Reviews can be sorted by highest rating, with reviews that have no rating handled as unrated entries.
- Highest-rated review pagination preserves the overall order across pages.
- Newest-first and oldest-first sorting continue to work.
- Invalid sorting options are rejected.

The activity tests also check the combination of rating and review contributions for a member, including cases where a movie has only a rating or only a review.

## 6. Regression Testing

Regression checks were included to make sure that existing behaviour remained available alongside the Streamlit integration features.

The selected test modules check, among other cases, that:

- Existing newest-first and oldest-first community review sorting continues to work after highest-rated sorting is supported at the application integration level.
- Rating-based movie ranking is applied to the complete filtered result set before pagination, rather than independently ranking each page.
- The catalogue's normal sorting responsibilities remain separate from community-rating ranking.
- Movies without ratings and reviews without associated star ratings are handled without treating missing values as valid ratings.
- Duplicate activity entries are avoided when a member has both a rating and a review for the same movie.
- Invalid inputs and unsupported sorting or limit values are handled through validation.

These checks help verify that the additional application behaviour does not remove or disrupt the existing catalogue, rating, review and activity workflows.

## 7. Testing Results and Limitations

All **12 selected automated test files** were executed successfully in the local development environment. The test files contain **70 test methods** covering authentication, homepage data, movie discovery, rating information, review integration, watched history and member activity.

The Streamlit application was also run locally and the main user-facing workflows were checked through the interface.

The automated tests primarily verify Python functions and database integration behaviour. They are not a complete browser-based UI automation suite and do not independently measure layout behaviour across different browsers or devices. Performance, response-time and concurrency analysis are documented separately in `performance_analysis.md`.

The following three test files are intentionally not repeated in this document because their testing information is maintained alongside the corresponding API documentation:

- `test_catalogue.py`
- `test_ratings_watchlist.py`
- `test_reviews.py`

---

**Related documentation**

- `docs/streamlit_implementation.md` – overview of the Streamlit application structure and behaviour.
- `docs/catalogue_api.md` – catalogue module functions and API details.
- `docs/ratings_watchlist_api.md` – rating, watchlist and watched-history operations.
- `docs/reviews_api.md` – community review operations.
- `performance_analysis.md` – backend performance and application performance observations.
