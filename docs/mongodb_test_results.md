# MongoDB Reviews — Testing Results

## 1. Overview

This document records the setup, conversion, unit-test and performance results for the MongoDB reviews module of the Netflix Review Application.

All results were produced on a local MongoDB Community Server and the local MariaDB `netflix_review_db` database, run from the repository root on 07/11/26.

## 2. Setup and Conversion Summary

| Step | Command | Result | Status |
|---|---|---|---|
| Create collection, validator and indexes | `python -m scripts.init_mongodb` | `reviews` collection with `$jsonSchema` validator; indexes `_id_`, `uniq_user_movie`, `movie_newest`, `review_text_search` | PASS |
| Convert review dataset | `python -m scripts.convert_reviews_to_mongo` | 20,000 rows read, 20,000 documents inserted, 0 skipped, 200 sample users | PASS |
| Convert movie catalogue | `python -m scripts.convert_movies_to_mongo` | 4,677 movies, 10,354 movie-genre links, 36,710 movie-actor links → 4,677 documents (counts match MariaDB) | PASS |

Every one of the 20,000 converted reviews was accepted by the `$jsonSchema` validator, and every `movie_id` exists in the MariaDB `movies` table.

## 3. Unit Tests

Command: `python -m tests.test_reviews`

Result: **13 tests run, 13 passed (OK).**

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
| `test_invalid_browse_parameters_raise` | Invalid `sort_by`, `limit` and `offset` values raise `ValueError` | PASS |
| `test_database_rejects_invalid_document` | Inserting a bad document directly (skipping the Python checks) is rejected by MongoDB's `$jsonSchema` validator | PASS |

The tests create two temporary MariaDB users and remove them and their reviews afterwards, using the same approach as `tests/test_ratings_watchlist.py`.

## 4. Performance Results

Command: `python -m scripts.performance_mongodb` (each query timed over 200 runs)

### Test 1: Index vs no index

Query: all reviews for movie `s4910`, newest first, in a collection of 20,000 reviews.

| Method | Plan | Returned | Docs examined | Keys examined | Avg time (ms) |
|---|---|---:|---:|---:|---:|
| No index (forced COLLSCAN) | SORT > COLLSCAN | 13 | 20,000 | 0 | 25.284 |
| `movie_newest` index | FETCH > IXSCAN | 13 | 13 | 13 | 0.933 |

The index made the query about **27x faster**. Without it, MongoDB read all 20,000 documents and then sorted the matches in memory. With the compound index on (`movie_id`, `created_at` descending), it read only the 13 matching entries, already in date order, so no SORT stage was needed.

### Test 2: SQL vs NoSQL

Query: all movies in the genre "Dramas".

| Method | Returned | Avg time (ms) |
|---|---:|---:|
| MariaDB: 3-table JOIN (`movies`, `movie_genres`, `genres`) | 2,039 | 6.800 |
| MongoDB: embedded `genres` array with multikey index | 2,039 | 10.388 |

Both databases returned the same 2,039 movies. MariaDB was faster for this bulk listing: the join uses small, indexed tables, while MongoDB has to return and decode 2,039 documents in Python. The embedded design's advantage is reading one movie's full details (title, genres and actors) in a single document read instead of three joined queries, not bulk filtering. Both databases ran locally, so the times include Python driver overhead.

## 5. Conclusion

All setup, conversion and unit tests passed. The validator, unique index and cross-database checks keep review data consistent, and the `movie_newest` index gives a large, measurable speed-up for the app's most common review query.
