# MongoDB Document Model — Reviews

## 1. Why reviews are in MongoDB

Ratings and watchlists have a fixed shape (a number or a yes/no per user and movie), so they stay in MariaDB tables. Reviews are different:

- The text length varies from two words to several paragraphs.
- Each review has a list of tags, from zero to three.
- Optional fields such as `updated_at` only exist on some reviews.

In MariaDB, the tags would need a separate `review_tags` table and a join. In MongoDB, one review is one **document** that holds its own tags array, so it is read and written in one operation.

MongoDB stores documents in a **collection**, not a table. There are no fixed columns: each document is a JSON-like (BSON) object. We add a validator so the collection still has rules (Section 4).

## 2. Collections

| Collection | Created by | Holds |
|---|---|---|
| `reviews` | `scripts/init_mongodb.py` | One document per review (the live collection used by the app) |
| `movies` | `scripts/convert_movies_to_mongo.py` | A copy of the MariaDB catalogue, one document per movie with `genres` and `actors` embedded as arrays. Used for `$lookup` (titles in statistics) and the SQL vs NoSQL comparison |

Database name: `netflix_review_db` (set by `MONGO_DB_NAME` in `.env`).

The sample dataset (`data/reviews.csv`) is a separate file. It only enters the `reviews` collection when `scripts/convert_reviews_to_mongo.py` is run, and that script only replaces reviews from `sample_user_...` accounts. Reviews written in the app by real users are kept.

## 3. Review document

```json
{
  "_id": ObjectId("..."),
  "user_id": 3,
  "movie_id": "s101",
  "review_text": "all is well!! classic",
  "spoiler": false,
  "tags": ["rewatchable"],
  "created_at": ISODate("2026-05-14T03:20:00Z"),
  "updated_at": ISODate("2026-06-01T10:00:00Z")
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `_id` | ObjectId | Auto | Created by MongoDB |
| `user_id` | int | Yes | Refers to `users.user_id` in MariaDB |
| `movie_id` | string | Yes | Refers to `movies.movie_id` in MariaDB, e.g. `"s101"` |
| `review_text` | string | Yes | 1 to 2,000 characters |
| `spoiler` | bool | Yes | `true` hides the review when "hide spoilers" is on |
| `tags` | array of strings | Yes | Lowercase, no duplicates, may be empty |
| `created_at` | date | Yes | Stored in UTC |
| `updated_at` | date | No | Only added when a review is edited |

## 4. Design decisions

| Decision | Choice | Reason |
|---|---|---|
| Embed or reference the movie? | **Reference** by `movie_id` | The catalogue already lives in MariaDB; copying title/genres into every review would go out of date |
| Embed or reference the user? | **Reference** by `user_id` | Users live in MariaDB, shared with ratings and watchlist |
| Tags | **Embedded array** | Tags belong to one review only; an array avoids a join table |
| IDs between databases | Same `movie_id` and `user_id` as MariaDB | Lets the app combine a movie's details, ratings and reviews |
| Rules | `$jsonSchema` validator | MongoDB is schema-less by default; the validator rejects wrong types, missing fields or empty text even if code skips the Python checks |
| Foreign keys | Checked in Python (`_user_and_movie_exist`) | MongoDB cannot enforce a foreign key to another database |

## 5. Indexes

| Index | Fields | Why |
|---|---|---|
| `_id_` | `_id` | Created automatically |
| `uniq_user_movie` | `user_id` + `movie_id`, unique | One review per user per movie (same rule as the `ratings` primary key); makes get/update/delete by user and movie fast |
| `movie_newest` | `movie_id` + `created_at` descending | The app's most common query, "all reviews for this movie, newest first", reads only the matching entries already in date order (see `docs/mongodb_test_results.md`) |

Not indexed on purpose: `tags` and `spoiler`. With 144 reviews, filtering a movie's few reviews by tag is already instant, and every extra index slows down inserts and updates.

## 6. Relational vs document terms

| MariaDB | MongoDB (this project) |
|---|---|
| Database `netflix_review_db` | Database `netflix_review_db` |
| Table | Collection (`reviews`, `movies`) |
| Row | Document |
| Column | Field |
| `review_tags` table + JOIN | Embedded `tags` array + `$unwind` |
| `GROUP BY` / `COUNT()` | `$group` / `$sum` |
| JOIN | `$lookup` |
| Primary key / UNIQUE | Unique index `uniq_user_movie` |
| Column types, NOT NULL | `$jsonSchema` validator |

## 7. Checking it in MongoDB Compass

1. Connect to `mongodb://localhost:27017`.
2. Open `netflix_review_db` → `reviews`.
3. **Documents** tab: browse the reviews. Filter example: `{ "movie_id": "s101" }`.
4. **Indexes** tab: `_id_`, `uniq_user_movie`, `movie_newest`.
5. **Validation** tab: shows the `$jsonSchema` rules.
6. **Aggregations** tab: paste a pipeline from `docs/advanced_query_results.md` to see its result.
