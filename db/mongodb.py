# MongoDB review functions
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, WriteError

from db.mariadb import get_connection

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "netflix_review_db")

MAX_REVIEW_LENGTH = 2000

# Validation rules enforced by MongoDB itself ($jsonSchema).
# Any insert or update that breaks these rules is rejected by the database.
REVIEW_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["user_id", "movie_id", "review_text", "spoiler", "tags", "created_at"],
        "properties": {
            "user_id": {"bsonType": "int", "minimum": 1},
            "movie_id": {"bsonType": "string", "pattern": "^s[0-9]+$", "maxLength": 10},
            "review_text": {"bsonType": "string", "minLength": 1, "maxLength": MAX_REVIEW_LENGTH},
            "spoiler": {"bsonType": "bool"},
            "tags": {"bsonType": "array", "items": {"bsonType": "string"}},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}

_client = None


# Returns the MongoDB database (one shared client for the whole app)
def get_mongo_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    return _client[MONGO_DB_NAME]


# Returns the reviews collection
def get_reviews_collection():
    return get_mongo_db()["reviews"]


# Creates the reviews collection with its validation rules and indexes.
# Safe to run more than once. reset=True deletes all existing reviews first.
def setup_reviews_collection(reset=False):
    db = get_mongo_db()

    if reset and "reviews" in db.list_collection_names():
        db["reviews"].drop()

    if "reviews" in db.list_collection_names():
        db.command("collMod", "reviews", validator=REVIEW_VALIDATOR)
    else:
        db.create_collection("reviews", validator=REVIEW_VALIDATOR)

    reviews = db["reviews"]

    # One review per user per movie (same rule as the ratings table's primary key)
    reviews.create_index([("user_id", ASCENDING), ("movie_id", ASCENDING)],
                         unique=True, name="uniq_user_movie")

    # Fast "all reviews for this movie, newest first"
    reviews.create_index([("movie_id", ASCENDING), ("created_at", DESCENDING)],
                         name="movie_newest")

    # Old keyword-search index from an earlier version (no longer used)
    if "review_text_search" in reviews.index_information():
        reviews.drop_index("review_text_search")


# ------------------------------------------------------------------------------------------------------
# Helpers

def _now():
    return datetime.now(timezone.utc)


# Checks user_id and movie_id types (same style as db/mariadb.py)
def _validate_ids(user_id, movie_id):
    if type(user_id) is not int or user_id < 1:
        raise ValueError("User ID must be a positive integer.")
    if not isinstance(movie_id, str) or movie_id.strip() == "":
        raise ValueError("Movie ID must be a non-empty string.")


def _validate_review_text(review_text):
    if not isinstance(review_text, str) or review_text.strip() == "":
        raise ValueError("Review text cannot be empty.")
    if len(review_text.strip()) > MAX_REVIEW_LENGTH:
        raise ValueError("Review text cannot be longer than 2000 characters.")


# Lowercases tags, removes blanks and duplicates
def _clean_tags(tags):
    if tags is None:
        return []
    if not isinstance(tags, list):
        raise ValueError("Tags must be a list of strings.")
    clean = []
    for tag in tags:
        if not isinstance(tag, str):
            raise ValueError("Tags must be a list of strings.")
        tag = tag.strip().lower()
        if tag != "" and tag not in clean:
            clean.append(tag)
    return clean


def _validate_limit_offset(limit, offset):
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise ValueError("limit must be an integer between 1 and 100")
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise ValueError("offset must be a non-negative integer")


# Cross-database check: MongoDB cannot enforce foreign keys to MariaDB,
# so the application checks that the user and movie exist before saving a review.
def _user_and_movie_exist(user_id, movie_id):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()

            cursor.execute("SELECT 1 FROM movies WHERE movie_id = %s", (movie_id,))
            movie = cursor.fetchone()

        return user is not None and movie is not None

    finally:
        connection.close()


# ------------------------------------------------------------------------------------------------------
# Reviews CRUD operations

# Adds a new review for a movie by a user.
# Returns True if added, False if the user has already reviewed this movie.
# Raises ValueError for invalid input or a user ID / movie ID that does not exist.
def add_review(user_id, movie_id, review_text, spoiler=False, tags=None):
    _validate_ids(user_id, movie_id)
    _validate_review_text(review_text)
    if not isinstance(spoiler, bool):
        raise ValueError("Spoiler must be True or False.")
    clean_tags = _clean_tags(tags)

    if not _user_and_movie_exist(user_id, movie_id):
        raise ValueError("Invalid user ID or movie ID.")

    review = {
        "user_id": user_id,
        "movie_id": movie_id,
        "review_text": review_text.strip(),
        "spoiler": spoiler,
        "tags": clean_tags,
        "created_at": _now(),
    }

    try:
        get_reviews_collection().insert_one(review)
        return True

    # Unique index uniq_user_movie: user has already reviewed this movie
    except DuplicateKeyError:
        return False

    # $jsonSchema validation failed
    except WriteError as error:
        raise ValueError("Review rejected by database validation.") from error


# Retrieves a user's review for a specific movie.
# Returns the review details or None if no review exists.
def get_review(user_id, movie_id):
    _validate_ids(user_id, movie_id)
    return get_reviews_collection().find_one(
        {"user_id": user_id, "movie_id": movie_id}, {"_id": 0})


# Updates an existing review. Only the fields given are changed.
# Only the author can update it, because the review is found by (user_id, movie_id).
# Returns True if a review was updated, else False.
def update_review(user_id, movie_id, review_text=None, spoiler=None, tags=None):
    _validate_ids(user_id, movie_id)

    changes = {}
    if review_text is not None:
        _validate_review_text(review_text)
        changes["review_text"] = review_text.strip()
    if spoiler is not None:
        if not isinstance(spoiler, bool):
            raise ValueError("Spoiler must be True or False.")
        changes["spoiler"] = spoiler
    if tags is not None:
        changes["tags"] = _clean_tags(tags)

    if len(changes) == 0:
        raise ValueError("Nothing to update.")
    changes["updated_at"] = _now()

    try:
        result = get_reviews_collection().update_one(
            {"user_id": user_id, "movie_id": movie_id}, {"$set": changes})
    except WriteError as error:
        raise ValueError("Review rejected by database validation.") from error

    return result.matched_count > 0


# Deletes a user's review for a specific movie.
# Returns True if a review was deleted, else False.
def delete_review(user_id, movie_id):
    _validate_ids(user_id, movie_id)
    result = get_reviews_collection().delete_one({"user_id": user_id, "movie_id": movie_id})
    return result.deleted_count > 0


# ------------------------------------------------------------------------------------------------------
# Browsing reviews

# Retrieves review documents for a movie, with optional spoiler/tag filtering
# and database-level date sorting and pagination.
# Rating lookup and highest-rated sorting are handled by the application layer.
def get_movie_reviews(movie_id, sort_by="newest", hide_spoilers=False, tag=None, limit=20, offset=0):
    if not isinstance(movie_id, str) or movie_id.strip() == "":
        raise ValueError("Movie ID must be a non-empty string.")

    if sort_by not in ("newest", "oldest"):
        raise ValueError("sort_by must be 'newest' or 'oldest'")

    _validate_limit_offset(limit, offset)

    query = {"movie_id": movie_id}

    if hide_spoilers:
        query["spoiler"] = False

    if tag:
        query["tags"] = tag.strip().lower()

    direction = DESCENDING if sort_by == "newest" else ASCENDING
    cursor = get_reviews_collection().find(query, {"_id": 0})
    cursor = cursor.sort("created_at", direction).skip(offset).limit(limit)

    return list(cursor)



# Retrieves all reviews written by one user, newest first.
def get_user_reviews(user_id, limit=20, offset=0):
    if type(user_id) is not int or user_id < 1:
        raise ValueError("User ID must be a positive integer.")
    _validate_limit_offset(limit, offset)

    cursor = get_reviews_collection().find({"user_id": user_id}, {"_id": 0})
    cursor = cursor.sort("created_at", DESCENDING).skip(offset).limit(limit)

    result = []
    for review in cursor:
        result.append(review)
    return result


# Finds reviews by movie title (partial, not case-sensitive), newest first.
# Titles live in the MariaDB movies table, so the matching movie_ids are looked up there first,
# then MongoDB returns their reviews. Each review gets a "title" field for display.
# Example: get_reviews_by_title("idiots") -> reviews of "3 Idiots"
def get_reviews_by_title(title_keyword, hide_spoilers=False, limit=20, offset=0):
    if not isinstance(title_keyword, str) or title_keyword.strip() == "":
        raise ValueError("Title keyword cannot be empty.")
    _validate_limit_offset(limit, offset)

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT movie_id, title FROM movies WHERE title LIKE %s",
                           ("%" + title_keyword.strip() + "%",))
            rows = cursor.fetchall()
    finally:
        connection.close()

    titles = {}
    for row in rows:
        titles[row["movie_id"]] = row["title"]
    if len(titles) == 0:
        return []

    query = {"movie_id": {"$in": list(titles.keys())}}
    if hide_spoilers:
        query["spoiler"] = False

    cursor = get_reviews_collection().find(query, {"_id": 0})
    cursor = cursor.sort("created_at", DESCENDING).skip(offset).limit(limit)

    result = []
    for review in cursor:
        review["title"] = titles[review["movie_id"]]
        result.append(review)
    return result


# Counts the number of reviews for a specific movie.
def get_review_count(movie_id):
    return get_reviews_collection().count_documents({"movie_id": movie_id})


# ------------------------------------------------------------------------------------------------------
# Advanced queries (aggregation pipelines)

# Movies with the most reviews.
# $lookup joins the "movies" collection (created by scripts/convert_movies_to_mongo.py)
# to show each movie's title.
def get_most_reviewed_movies(limit=10):
    _validate_limit_offset(limit, 0)
    pipeline = [
        {"$group": {
            "_id": "$movie_id",
            "review_count": {"$sum": 1},
            "spoiler_count": {"$sum": {"$cond": ["$spoiler", 1, 0]}},
            "latest_review": {"$max": "$created_at"},
        }},
        {"$sort": {"review_count": -1, "_id": 1}},
        {"$limit": limit},
        {"$lookup": {"from": "movies", "localField": "_id",
                     "foreignField": "movie_id", "as": "movie"}},
    ]

    result = []
    for row in get_reviews_collection().aggregate(pipeline):
        title = None
        if len(row["movie"]) > 0:
            title = row["movie"][0]["title"]
        result.append({
            "movie_id": row["_id"],
            "title": title,
            "review_count": row["review_count"],
            "spoiler_count": row["spoiler_count"],
            "latest_review": row["latest_review"],
        })
    return result


# Most used review tags across all reviews.
# $unwind splits each review's tags array into one row per tag, then $group counts them.
def get_popular_tags(limit=10):
    _validate_limit_offset(limit, 0)
    pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1, "_id": 1}},
        {"$limit": limit},
    ]

    result = []
    for row in get_reviews_collection().aggregate(pipeline):
        result.append({"tag": row["_id"], "count": row["count"]})
    return result


if __name__ == "__main__":
    get_mongo_db().command("ping")
    print("MongoDB connection successful!")
