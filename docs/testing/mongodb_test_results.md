# MongoDB Reviews — Testing Results

## 1. Overview

This document records the setup, conversion, unit-test and performance results for the MongoDB reviews module of the Netflix Review Application.

All results were produced on a local MongoDB Community Server and the local MariaDB `netflix_review_db` database, run from the repository root on 11/11/26 with the review dataset `data/reviews.csv` loaded (144 reviews, 11 sample users). The movie catalogue conversion was run on 07/11/26.

## 2. Setup and Conversion Summary

| Step | Command | Result | Status |
|---|---|---|---|
| Create collection, validator and indexes | `python -m scripts.init_mongodb --reset` | `reviews` collection with `$jsonSchema` validator; indexes `_id_`, `uniq_user_movie`, `movie_newest` | PASS |
| Convert review dataset | `python -m scripts.convert_reviews_to_mongo` | 144 rows read, 144 documents inserted, 0 skipped; 11 sample users; 189 unused sample users from the earlier 20,000-review version removed from MariaDB | PASS |
| Convert movie catalogue | `python -m scripts.convert_movies_to_mongo` | 4,677 movies, 10,354 movie-genre links, 36,710 movie-actor links → 4,677 documents (counts match MariaDB) | PASS |

## 3. Unit Tests

Command: `python -m tests.test_reviews`

Result: **14 tests run, 14 passed (OK).**

| Test | What it checks | Status |
|---|---|---|
| `test_add_and_get_review` | A review is added and read back; tags are lowercased and de-duplicated | PASS |
| `test_duplicate_review_returns_false` | A second review by the same user for the same movie returns `False` (unique index) | PASS |
| `test_invalid_user_or_movie_raises` | A user ID or movie ID that is not in MariaDB raises `ValueError` (cross-database check) | PASS |
| `test_invalid_input_raises` | Empty text, text over 2,000 characters, a non-bool spoiler and a string user ID raise `ValueError` | PASS |
| `test_get_missing_review_returns_none` | Reading a review that does not exist returns `None` | PASS |
| `test_update_review` | Text and spoiler flag are updated and `updated_at` is added | PASS |
| `test_other_user_cannot_update_or_delete` | Another user cannot edit or delete the author's review | PASS |
| `test_update_with_nothing_raises` | An update with no fields raises `ValueError` | PASS |
| `test_delete_review` | A review is deleted; deleting it again returns `False` | PASS |
| `test_movie_reviews_hide_spoilers_and_tag` | Spoiler reviews are hidden on request; tag filtering is not case-sensitive | PASS |
| `test_user_reviews_and_count` | A user's reviews and a movie's review count are correct | PASS |
| `test_reviews_by_title` | Searching by title ("1920") returns only that movie's reviews with its title; an unknown title returns `[]`; an empty keyword raises `ValueError` | PASS |
| `test_invalid_browse_parameters_raise` | Invalid `sort_by`, `limit` and `offset` values raise `ValueError` | PASS |
| `test_database_rejects_invalid_document` | Inserting a bad document directly (skipping the Python checks) is rejected by MongoDB's `$jsonSchema` validator | PASS |

The tests create two temporary MariaDB users and remove them and their reviews afterwards, using the same approach as `tests/test_ratings_watchlist.py`.

## 4. Performance Results

Command: `python -m scripts.performance_mongodb` (each query timed over 200 runs)


### Test 1: Index vs no index

Query: all reviews for movie `s28` (#Alive), newest first, in a collection of 144 reviews.

| Method | Plan | Returned | Docs examined | Keys examined | Avg time (ms) |
|---|---|---:|---:|---:|---:|
| No index (forced COLLSCAN) | SORT > COLLSCAN | 4 | 144 | 0 | 2.001 |
| `movie_newest` index | FETCH > IXSCAN | 4 | 4 | 4 | 1.283 |

The index made the query about **1.6x faster**. Without it, MongoDB read all 144 documents and then sorted the 4 matches in memory (SORT stage). With the compound index on (`movie_id`, `created_at` descending), it read only the 4 matching entries, already in date order, so no SORT stage was needed.

The time saved is small because the collection only has 144 reviews, so a full scan is already fast. The documents examined (144 → 4) show how the index scales: a full scan grows with the whole collection, while the index only reads the reviews of the movie asked for. An earlier test with 20,000 generated reviews showed 20,000 → 13 documents examined and about 27x faster.

### Test 2: SQL vs NoSQL (all movies in the genre "Dramas")

| Method | Returned | Avg time (ms) |
|---|---:|---:|
| MariaDB: 3-table JOIN | 2,039 | 20.133 |
| MongoDB: embedded `genres` array with multikey index | 2,039 | 19.559 |

Both return the same 2,039 movies in about the same time (MongoDB about 3% faster on 11/11/26; on 07/11/26 MariaDB was faster, 6.8 ms vs 10.4 ms). For a bulk listing like this the difference is small and changes between runs, because both databases run locally and the times include Python driver overhead. The embedded design's real advantage is reading one movie's full details (genres and actors) in a single document read instead of three joined tables.

## 5. Conclusion

All setup and unit tests passed. The validator, unique index and cross-database checks keep review data consistent, and the `movie_newest` index cuts the documents examined for the app's most common review query from the whole collection (144) to only the matching reviews (4), with a speed-up that grows as the collection grows.
