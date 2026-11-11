# MongoDB Reviews — Handover for the Streamlit App

For Nusrat (Streamlit). Everything needed to run the reviews module on your laptop and call it from the app. Full details of each function are in `docs/reviews_api.md`.

## 1. One-time setup

1. Install **MongoDB Community Server** (it runs at `mongodb://localhost:27017`). Compass is optional, for looking at the data.
2. Install the Python packages:

```powershell
pip install pymongo python-dotenv
```

3. In your own `.env` file (copied from `.env.example`), make sure these two lines exist:

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=netflix_review_db
```

No password is needed for a local MongoDB. Never commit `.env`; only `.env.example` is in the repo.

4. MariaDB must already be set up with the catalogue imported (`python -m scripts.import_movies`), because reviews refer to MariaDB users and movies.

5. From the repository root, run in this order:

```powershell
python -m scripts.init_mongodb
python -m scripts.convert_reviews_to_mongo
python -m scripts.convert_movies_to_mongo
```

Expected: the collection is created with indexes `_id_, uniq_user_movie, movie_newest`, 144 reviews are inserted and 0 are skipped, and the movie count matches MariaDB.

6. Check everything works:

```powershell
python -m tests.test_reviews
```

Expected: all tests pass (`OK`). The tests make two temporary users and delete them afterwards.

## 2. Import

```python
from db.mongodb import (
    add_review, get_review, update_review, delete_review,
    get_movie_reviews, get_user_reviews, get_review_count, get_reviews_by_title,
    get_most_reviewed_movies, get_popular_tags,
)
```

## 3. Function contracts

| Function | Returns | Errors |
|---|---|---|
| `add_review(user_id, movie_id, review_text, spoiler=False, tags=None)` | `True` added · `False` this user already reviewed this movie | `ValueError`: bad input, text over 2,000 chars, unknown user/movie |
| `get_review(user_id, movie_id)` | review `dict` or `None` | `ValueError`: bad IDs |
| `update_review(user_id, movie_id, review_text=None, spoiler=None, tags=None)` | `True` updated · `False` no such review | `ValueError`: nothing to update or bad input |
| `delete_review(user_id, movie_id)` | `True` deleted · `False` no such review | `ValueError`: bad IDs |
| `get_movie_reviews(movie_id, sort_by="newest", hide_spoilers=False, tag=None, limit=20, offset=0)` | `list` of review dicts | `ValueError`: `sort_by` not newest/oldest, `limit` not 1–100, negative `offset` |
| `get_user_reviews(user_id, limit=20, offset=0)` | `list`, newest first | `ValueError` |
| `get_review_count(movie_id)` | `int` | — |
| `get_reviews_by_title(title_keyword, hide_spoilers=False, limit=20, offset=0)` | `list`, each with an extra `title` | `ValueError`: empty keyword |
| `get_most_reviewed_movies(limit=10)` | `list` of `{movie_id, title, review_count, spoiler_count, latest_review}` | `ValueError` |
| `get_popular_tags(limit=10)` | `list` of `{tag, count}` | `ValueError` |

Rules to remember:
- `user_id` is an **int**; `movie_id` is a **string** like `"s101"` (the same ID the catalogue uses).
- Only the author can edit or delete, because reviews are found by (`user_id`, `movie_id`).
- Tags are a list of strings, e.g. `["acting", "ending"]`; they are lowercased automatically.
- Each review dict has `created_at` (and `updated_at` if edited) as a Python `datetime` in UTC.

## 4. Sample calls

```python
add_review(1, "s101", "So funny and so true about school pressure", tags=["funny"])
# True

add_review(1, "s101", "Posting again")
# False  (already reviewed)

get_review(1, "s101")
# {'user_id': 1, 'movie_id': 's101', 'review_text': 'So funny and ...', 'spoiler': False,
#  'tags': ['funny'], 'created_at': datetime(...)}

update_review(1, "s101", spoiler=True)
# True

get_movie_reviews("s101", hide_spoilers=True, limit=5)
# [ ...up to 5 non-spoiler reviews, newest first... ]

get_reviews_by_title("idiots")
# [ ...reviews of "3 Idiots", each with 'title': '3 Idiots'... ]

get_most_reviewed_movies(5)
# [{'movie_id': 's101', 'title': '3 Idiots', 'review_count': 4, ...}, ...]

get_popular_tags(5)
# [{'tag': 'story', 'count': ...}, ...]

delete_review(1, "s101")
# True
```

## 5. Streamlit example (movie details page)

```python
import streamlit as st
from db.mongodb import add_review, get_movie_reviews

movie_id = "s101"
user_id = st.session_state.get("user_id")   # however the app stores the logged-in user

hide = st.checkbox("Hide spoilers")
for review in get_movie_reviews(movie_id, hide_spoilers=hide):
    st.write(review["review_text"])
    st.caption(", ".join(review["tags"]) + " · " + review["created_at"].strftime("%d/%m/%y"))

with st.form("review_form"):
    text = st.text_area("Your review")
    spoiler = st.checkbox("Contains spoilers")
    if st.form_submit_button("Post review"):
        try:
            if add_review(user_id, movie_id, text, spoiler=spoiler):
                st.success("Review posted")
            else:
                st.warning("You already reviewed this movie. Edit your review instead.")
        except ValueError as error:
            st.error(str(error))
```

## 6. If something goes wrong

| Message | Fix |
|---|---|
| `ServerSelectionTimeoutError` | MongoDB is not running. Start the MongoDB service (Windows: Services → MongoDB Server → Start) |
| `ModuleNotFoundError: No module named 'db'` | Run commands from the repository root with `python -m ...` |
| `ValueError: Invalid user ID or movie ID.` | The user or movie is not in your MariaDB; import the catalogue / create the user first |
| `Review rejected by database validation.` | The data broke the `$jsonSchema` rules (e.g. wrong type) |
| Most-reviewed `title` is `None` | Run `python -m scripts.convert_movies_to_mongo` (the `movies` collection is missing) |

Contact: Weibin (Member 3, MongoDB reviews).
