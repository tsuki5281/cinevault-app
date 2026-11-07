# Advanced MongoDB Queries — Testing Results

## 1. Overview

This document records the advanced MongoDB queries implemented in `db/mongodb.py` and their results on the sample dataset (20,000 reviews, 4,677 movies), run on 07/11/26.

The `movies` collection used by `$lookup` is created by `scripts/convert_movies_to_mongo.py`.

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

| Feature | Purpose |
|---|---|
| `$group` + `$sum` | Counts reviews per movie (like SQL `GROUP BY` + `COUNT`) |
| `$cond` | Counts only reviews where `spoiler` is true (like SQL `SUM(CASE WHEN ...)`) |
| `$max` | Finds the latest review date |
| `$sort` + `$limit` | Returns the top 5 |
| `$lookup` | Joins the `movies` collection to get each title (like SQL `JOIN`) |

### Result — `get_most_reviewed_movies(5)`

| movie_id | Title | Reviews | Spoilers | Latest review |
|---|---|---:|---:|---|
| s2729 | High End Yaariyan | 13 | 5 | 12/08/26 |
| s4910 | Popeye | 13 | 2 | 01/11/26 |
| s2609 | Happy Anniversary | 12 | 1 | 31/10/26 |
| s2923 | I'm Brent Morin | 12 | 2 | 01/11/26 |
| s4750 | Pan's Labyrinth | 12 | 4 | 18/08/26 |

## 3. Reviews per Genre

### Purpose

Counts reviews per genre. Genres are not stored in the review documents, so the pipeline joins each review to its movie and then splits the movie's `genres` array.

### Pipeline

```python
[
    {"$lookup": {"from": "movies", "localField": "movie_id",
                 "foreignField": "movie_id", "as": "movie"}},
    {"$unwind": "$movie"},
    {"$unwind": "$movie.genres"},
    {"$group": {
        "_id": "$movie.genres",
        "review_count": {"$sum": 1},
        "spoiler_count": {"$sum": {"$cond": ["$spoiler", 1, 0]}},
    }},
    {"$sort": {"review_count": -1, "_id": 1}},
    {"$limit": 5},
]
```

### MongoDB Features Used

| Feature | Purpose |
|---|---|
| `$lookup` | Joins each review to its movie document |
| `$unwind` (twice) | Turns the joined array into one document, then one row per genre |
| `$group` + `$cond` | Counts reviews and spoilers per genre |

### Result — `get_reviews_per_genre(5)`

| Genre | Reviews | Spoilers |
|---|---:|---:|
| International Movies | 9,387 | 1,429 |
| Dramas | 8,616 | 1,329 |
| Comedies | 5,909 | 914 |
| Action & Adventure | 2,972 | 446 |
| Independent Movies | 2,866 | 451 |

A movie can belong to several genres, so these counts add up to more than 20,000.

## 4. Popular Tags

### Purpose

Finds the most used review tags by splitting each review's `tags` array.

### Pipeline

```python
[
    {"$unwind": "$tags"},
    {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
    {"$sort": {"count": -1, "_id": 1}},
    {"$limit": 5},
]
```

### Result — `get_popular_tags(5)`

| Tag | Count |
|---|---:|
| visuals | 2,636 |
| acting | 2,569 |
| ending | 2,562 |
| funny | 2,535 |
| overrated | 2,523 |

In SQL, tags would need a separate `review_tags` table and a join. In MongoDB, the array is stored inside the review and `$unwind` splits it at query time.

## 5. Reviews per Month

### Purpose

Shows review activity over time by grouping on the year and month of `created_at`.

### Pipeline

```python
[
    {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}},
                "count": {"$sum": 1}}},
    {"$sort": {"_id": 1}},
]
```

### Result — `get_reviews_per_month()` (first 6 months)

| Month | Reviews |
|---|---:|
| 2025-01 | 916 |
| 2025-02 | 888 |
| 2025-03 | 896 |
| 2025-04 | 914 |
| 2025-05 | 917 |
| 2025-06 | 911 |

The counts are steady because the sample review dates are spread evenly between January 2025 and November 2026.

## 6. Keyword Search (Text Index)

### Purpose

Searches review text for a keyword using the `review_text_search` text index and ranks results by relevance score.

### Query

```python
reviews.find({"$text": {"$search": "twist"}},
             {"score": {"$meta": "textScore"}}).sort([("score", {"$meta": "textScore"})])
```

### Result — `search_reviews("twist", 3)`

| user_id | movie_id | Spoiler | Score | Review text (start) |
|---:|---|---|---:|---|
| 258 | s1487 | True | 0.545 | "Honestly, this dramas pick was one where the plot was predictable..." |
| 13 | s4228 | True | 0.545 | "Surprisingly, this dramas pick was one where the soundtrack was great..." |
| 46 | s1789 | True | 0.545 | "Surprisingly, this dramas pick was one where it was really enjoyable..." |

All three matches contain "The twist at the end changes everything." and are correctly flagged as spoilers. A SQL `LIKE '%twist%'` cannot use a normal index; the text index also handles word stemming and relevance ranking.

## 7. Conclusion

All five advanced queries ran successfully on the sample data. Together they show MongoDB's aggregation framework (`$group`, `$cond`, `$unwind`, `$lookup`, `$dateToString`) and text search as the NoSQL equivalents of SQL `GROUP BY`, `CASE`, `JOIN` and full-text search.
