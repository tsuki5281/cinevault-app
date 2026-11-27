# Advanced MongoDB Queries — Testing Results

## 1. Overview

This document records the two advanced MongoDB queries implemented in `db/mongodb.py` for the Netflix Review Application, with their results on the review dataset (`data/reviews.csv`: 144 reviews, 100 movies, 11 sample users), run on 11/11/26.

Both queries use MongoDB's aggregation framework.

To print the results, run from the repository root:

```powershell
python -c "from db.mongodb import *; print(get_most_reviewed_movies(5)); print(get_popular_tags(5))"
```

## 2. Most-Reviewed Movies

### Purpose

Finds the movies with the most reviews, with their spoiler count and latest review date, and joins the `movies` collection to show each title.

### Pipeline

```python
[
    {"$group": {
        "_id": "$movie_id",
        "review_count": {"$sum": 1},
        "spoiler_count": {"$sum": {"$cond": ["$spoiler", 1, 0]}},
        "latest_review": {"$max": "$created_at"},
    }},
    {"$sort": {"review_count": -1, "_id": 1}},
    {"$limit": 5},
    {"$lookup": {"from": "movies", "localField": "_id",
                 "foreignField": "movie_id", "as": "movie"}},
]
```

### MongoDB Features Used

| Feature | Purpose | SQL equivalent |
|---|---|---|
| `$group` + `$sum` | Counts reviews per movie | `GROUP BY` + `COUNT()` |
| `$cond` | Counts only reviews where `spoiler` is true | `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` |
| `$max` | Finds the latest review date | `MAX()` |
| `$sort` + `$limit` | Returns the top 5 | `ORDER BY` + `LIMIT` |
| `$lookup` | Joins the `movies` collection to get each title | `JOIN` |

### Result — `get_most_reviewed_movies(5)`

| movie_id | Title | Reviews | Spoilers | Latest review |
|---|---|---:|---:|---|
| `s101` | 3 Idiots | 4 | 0 | 28/08/26 |
| `s28` | #Alive | 4 | 1 | 16/05/26 |
| `s107` | 365 Days | 3 | 0 | 29/05/26 |
| `s122` | 50 First Dates | 3 | 1 | 15/06/26 |
| `s128` | 6 Underground | 3 | 1 | 27/07/26 |

Movies with the same review count are ordered by `movie_id` (the second sort key), so 3 Idiots (`s101`) comes before #Alive (`s28`) because the IDs are compared as text. Dates are stored in UTC and shown here in Singapore time.

## 3. Popular Tags

### Purpose

Finds the most used review tags. Each review stores its tags as an array. The tags were assigned by `scripts/tag_reviews.py`, which gives a tag only when one of its keywords appears in that review's text.

### Pipeline

```python
[
    {"$unwind": "$tags"},
    {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
    {"$sort": {"count": -1, "_id": 1}},
    {"$limit": 5},
]
```

### MongoDB Features Used

| Feature | Purpose | SQL equivalent |
|---|---|---|
| `$unwind` | Splits each review's `tags` array into one row per tag | A separate `review_tags` table + `JOIN` |
| `$group` + `$sum` | Counts how often each tag is used | `GROUP BY` + `COUNT()` |
| `$sort` + `$limit` | Returns the top 5 | `ORDER BY` + `LIMIT` |

In SQL, tags would need their own table and a join. In MongoDB, the array is stored inside the review document and split at query time with `$unwind`.

### Result — `get_popular_tags(5)`

| Tag | Count |
|---|---:|
| story | 38 |
| funny | 37 |
| emotional | 35 |
| pacing | 23 |
| characters | 19 |

The counts add up to more than 144 because one review can have up to 3 tags. 7 reviews have no tags and are dropped by `$unwind`.
