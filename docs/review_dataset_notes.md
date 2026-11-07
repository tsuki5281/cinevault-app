# Review Dataset Notes

## 1. Why the reviews are generated

Netflix does not publish user reviews, and the catalogue dataset has no review text. The project FAQ allows generated data when an application needs user data that cannot be found elsewhere, so the review dataset is generated from the real movie catalogue.

## 2. Files

| File | Purpose |
|---|---|
| `data/reviews.csv` | The review dataset (20,000 rows) |
| `scripts/generate_review_dataset.py` | Creates `data/reviews.csv` from `data/netflix_movies_cleaned.csv` |
| `scripts/convert_reviews_to_mongo.py` | Converts the CSV into MongoDB documents in the `reviews` collection |

## 3. Fields

| CSV column | Example | MongoDB field | Converted to |
|---|---|---|---|
| `username` | `sample_user_01` | `user_id` | int, looked up in the MariaDB `users` table (created if missing) |
| `movie_id` | `s10` | `movie_id` | string, must exist in the MariaDB `movies` table |
| `review_text` | `Honestly, this dramas pick was one where...` | `review_text` | string, 1 to 2,000 characters |
| `spoiler` | `False` | `spoiler` | bool |
| `tags` | `acting;ending` | `tags` | array of lowercase strings |
| `created_at` | `2026-03-01T14:05:00Z` | `created_at` | BSON date (UTC) |

## 4. Assumptions

- 200 sample users (`sample_user_01` to `sample_user_200`) each review 100 different movies, giving 20,000 reviews (about 4 per movie on average), enough for a realistic demo and a measurable index speed-up.
- Each user reviews a movie at most once, matching the unique index on (`user_id`, `movie_id`).
- Movies are picked only from the 4,677 cleaned movies, so every `movie_id` exists in MariaDB.
- The CSV stores usernames instead of user IDs, because `users.user_id` is AUTO_INCREMENT and can differ between team members' local databases. The conversion script maps usernames to each member's own IDs.
- About 60% of reviews are positive, about 15% are marked as spoilers, and each review has 0 to 3 tags.
- Review dates are spread between 1 Jan 2025 and 1 Nov 2026.
- `random.seed(42)` makes the dataset identical every time it is generated.

## 5. How to rebuild

```powershell
python -m scripts.generate_review_dataset
python -m scripts.init_mongodb
python -m scripts.convert_reviews_to_mongo
```
