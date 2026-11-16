# Review Dataset Notes

## 1. Why we made our own reviews

Netflix does not publish user reviews, and the catalogue dataset has no review text. The project FAQ allows us to create our own data when the application needs user data that cannot be found elsewhere, so the team made a small review dataset for the first 100 movies.

## 2. Scope

| Item | Value |
|---|---|
| Movies | The first 100 movies in `data/netflix_movies_cleaned.csv` (`s2` to `s148`) |
| Reviews | 144 (1 to 4 per movie, so the "most reviewed movies" query has a clear ranking) |
| Users | 11 sample users: `sample_user_01` to `sample_user_10` write casual reviews; `sample_user_11` writes longer, critic-style reviews |
| Spoilers | 29 reviews are marked as spoilers |
| Dates | `created_at` between 01/01/25 and 31/10/26 (Singapore time) |
| File | `data/reviews.csv` |

## 3. How the reviews were made

1. For each movie, the review was based on its title, genres and official Netflix description in `data/netflix_movies_cleaned.csv`.
2. Spoiler reviews: 29 movies were picked down the list using the digits of π as the gaps between picks (e.g. 3, 1, 4, 1, 5…), so the choice was not hand-picked. For each one, a review revealing a real plot point (such as the ending or a twist) was written after checking published plot summaries, and its `spoiler` column was set to `Yes`. All other reviews avoid plot details beyond the official description.
3. Tags were not chosen by hand. `scripts/tag_reviews.py` gives a review a tag only when one of that tag's keywords appears in the review text (for example "jump scares" → `scary`, "the cast" → `acting`), up to 3 tags per review. 7 reviews mention no keyword (e.g. "just horrible") and have no tags.
4. The `created_at` dates were generated randomly (with a fixed seed) inside the date range above, so the "newest first" ordering has realistic, varied dates.

## 4. Fields

| CSV column | Example | MongoDB field | Converted to |
|---|---|---|---|
| `movie_id` | `s3` | `movie_id` | string, must exist in the MariaDB `movies` table |
| `title` | `23:59` | (not stored) | for reading the CSV only; the app gets titles from the catalogue |
| `username` | `sample_user_01` | `user_id` | int, looked up in the MariaDB `users` table (created if missing) |
| `review_text` | `ngl the earthquake was surreal` | `review_text` | string, 1 to 2,000 characters |
| `spoiler` | `No` | `spoiler` | bool |
| `tags` | `story;scary` | `tags` | array of lowercase strings (can be empty) |
| `created_at` | `2025-11-28 12:25` | `created_at` | BSON date, Singapore time converted to UTC |

## 5. Tag vocabulary

`acting`, `story`, `ending`, `pacing`, `visuals`, `music`, `funny`, `scary`, `emotional`, `action`, `family`, `characters`, `realistic`, `rewatchable`, `overrated`. The keywords for each tag are listed in `TAG_KEYWORDS` in `scripts/tag_reviews.py`.

## 6. Why usernames instead of user IDs

`users.user_id` is AUTO_INCREMENT, so the same user can get a different ID in each team member's local database. The CSV stores usernames, and `scripts/convert_reviews_to_mongo.py` looks up each member's own IDs.

## 7. How to load it

```powershell
python -m scripts.init_mongodb
python -m scripts.convert_reviews_to_mongo
```

The conversion script skips and reports any invalid row with its CSV line number. It also replaces older sample reviews and removes sample users from older dataset versions that have no ratings or watchlist entries.

To re-tag after editing review text:

```powershell
python -m scripts.tag_reviews data/reviews.csv
```

Tip: avoid opening and saving `reviews.csv` in Excel. Excel changes the date format and some titles (e.g. `07:19` becomes `7:19`). The conversion script still accepts Excel's date format, but the file is cleaner without it.

## 8. Earlier version

An earlier version generated 20,000 reviews automatically from random template sentences and random tags (`scripts/generate_review_dataset.py`, now removed). It was replaced because the review text and tags did not match the movies, and the team asked for a smaller dataset of about 10 users and the first 100 movies.
