# Conversion script: data/reviews.csv (review dataset) -> MongoDB "reviews" documents
#
# The CSV is flat text. Each row is checked and converted into a typed MongoDB document:
#   username "sample_user_01"   -> user_id (looked up / created in the MariaDB users table)
#   spoiler  "Yes" / "No"       -> True / False                (bool)
#   tags     "acting;ending"    -> ["acting", "ending"]        (array, can be empty)
#   created_at "2026-03-01 14:05" (Singapore time) -> datetime (BSON date, stored in UTC)
# Invalid rows are skipped and reported with their CSV line number.
#
# Sample reviews imported here are also added to MariaDB's watched_movies table.
# This keeps imported demo reviews consistent with reviews submitted in the app.
#
# Run from the repository root (after scripts.import_movies and scripts.init_mongodb):
#   python -m scripts.convert_reviews_to_mongo

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

from db.mariadb import get_connection
from db.mongodb import MAX_REVIEW_LENGTH, get_reviews_collection, setup_reviews_collection

BASE_DIR = Path(__file__).resolve().parent.parent
REVIEWS_CSV = BASE_DIR / "data" / "reviews.csv"
USERNAME_PREFIX = "sample_user_"
SINGAPORE = timezone(timedelta(hours=8))

# Date formats accepted in the created_at column.
# The last ones are what Excel writes if the CSV is opened and saved in Excel.
DATE_FORMATS = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d",
                "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y"]


# Reads the CSV rows as dictionaries and remembers each row's line number
def read_csv_rows():
    rows = []
    # utf-8-sig also removes the hidden "BOM" character Excel adds at the start of the file
    with open(REVIEWS_CSV, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for name in ["movie_id", "username", "review_text", "spoiler", "tags", "created_at"]:
            if name not in reader.fieldnames:
                raise RuntimeError(f"Column '{name}' not found in data/{REVIEWS_CSV.name}.")

        line_number = 1
        for row in reader:
            line_number = line_number + 1
            # Skip completely empty lines
            if row["movie_id"].strip() == "" and row["review_text"].strip() == "":
                continue
            row["line_number"] = line_number
            rows.append(row)

    return rows


# Returns the set of movie_ids that exist in MariaDB
def get_movie_ids():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT movie_id FROM movies")
            rows = cursor.fetchall()
    finally:
        connection.close()

    movie_ids = set()
    for row in rows:
        movie_ids.add(row["movie_id"])
    return movie_ids


# Creates any missing users and returns a {username: user_id} lookup
def get_user_ids(usernames):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            for username in usernames:
                cursor.execute("INSERT IGNORE INTO users (username) VALUES (%s)", (username,))

            user_ids = {}
            for username in usernames:
                cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                user_ids[username] = cursor.fetchone()["user_id"]

        connection.commit()
        return user_ids

    finally:
        connection.close()


# Returns the user_ids of every sample user (sample_user_...) in MariaDB
def get_all_sample_user_ids():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE username LIKE %s",
                           (USERNAME_PREFIX + "%",))
            rows = cursor.fetchall()
    finally:
        connection.close()

    user_ids = []
    for row in rows:
        user_ids.append(row["user_id"])
    return user_ids


# Adds each imported sample review's movie to the user's watched history.
# INSERT IGNORE makes this safe to run repeatedly and preserves existing timestamps.
def sync_sample_reviews_to_watched_history(documents):
    if not documents:
        return 0

    watched_pairs = list(dict.fromkeys(
        (document["user_id"], document["movie_id"])
        for document in documents
    ))

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT IGNORE INTO watched_movies (user_id, movie_id)
                VALUES (%s, %s)
                """,
                watched_pairs
            )
            inserted = cursor.rowcount

        connection.commit()
        return inserted

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# Deletes sample users from older dataset versions (e.g. sample_user_12 to sample_user_200).
# A user is only deleted if they are not in the current dataset and have no ratings,
# watchlist rows or watched-history rows.
def remove_unused_sample_users(current_usernames):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, username FROM users WHERE username LIKE %s",
                           (USERNAME_PREFIX + "%",))
            rows = cursor.fetchall()

            removed = 0
            for row in rows:
                if row["username"] in current_usernames:
                    continue
                cursor.execute(
                    "DELETE FROM users WHERE user_id = %s "
                    "AND NOT EXISTS (SELECT 1 FROM ratings WHERE ratings.user_id = %s) "
                    "AND NOT EXISTS (SELECT 1 FROM watchlist WHERE watchlist.user_id = %s) "
                    "AND NOT EXISTS (SELECT 1 FROM watched_movies WHERE watched_movies.user_id = %s)",
                    (row["user_id"], row["user_id"], row["user_id"], row["user_id"]))
                removed = removed + cursor.rowcount

        connection.commit()
        return removed

    finally:
        connection.close()


# Turns the created_at text into a datetime, or None if the cell is empty.
# Raises ValueError if the text is not a date in one of DATE_FORMATS.
def parse_date(text):
    text = text.strip()
    if text == "":
        return None

    for date_format in DATE_FORMATS:
        try:
            local_time = datetime.strptime(text, date_format).replace(tzinfo=SINGAPORE)
            return local_time.astimezone(timezone.utc)
        except ValueError:
            pass

    raise ValueError(f"created_at '{text}' is not a date like 2026-03-01 14:05")


# Splits "acting;ending" (or "acting, ending") into a clean list
def parse_tags(text):
    tags = []
    for tag in text.replace(",", ";").split(";"):
        tag = tag.strip().lower()
        if tag != "" and tag not in tags:
            tags.append(tag)
    return tags


# Returns a list of problems with one row (empty list = row is valid)
def check_row(row, movie_ids, seen_pairs):
    problems = []
    movie_id = row["movie_id"].strip()
    username = row["username"].strip()
    review_text = row["review_text"].strip()
    spoiler = row["spoiler"].strip().lower()

    if movie_id not in movie_ids:
        problems.append(f"movie_id '{movie_id}' is not in the movies table")
    if not username.startswith(USERNAME_PREFIX):
        problems.append(f"username '{username}' should look like sample_user_01")
    if review_text == "":
        problems.append("review_text is empty")
    if len(review_text) > MAX_REVIEW_LENGTH:
        problems.append("review_text is longer than 2,000 characters")
    if spoiler not in ("yes", "no", ""):
        problems.append("spoiler must be Yes or No")
    try:
        parse_date(row["created_at"])
    except ValueError as error:
        problems.append(str(error))

    pair = (username, movie_id)
    if pair in seen_pairs:
        problems.append(f"{username} already reviewed {movie_id} (line {seen_pairs[pair]})")
    else:
        seen_pairs[pair] = row["line_number"]

    return problems


# Converts one valid CSV row into a typed review document
def convert_row(row, user_ids, conversion_time):
    created_at = parse_date(row["created_at"])
    if created_at is None:
        created_at = conversion_time

    return {
        "user_id": user_ids[row["username"].strip()],
        "movie_id": row["movie_id"].strip(),
        "review_text": row["review_text"].strip(),
        "spoiler": row["spoiler"].strip().lower() == "yes",
        "tags": parse_tags(row["tags"]),
        "created_at": created_at,
    }


def main():
    setup_reviews_collection()

    rows = read_csv_rows()
    print(f"Read {len(rows)} rows from data/{REVIEWS_CSV.name}")

    movie_ids = get_movie_ids()
    seen_pairs = {}
    valid_rows = []
    for row in rows:
        problems = check_row(row, movie_ids, seen_pairs)
        if len(problems) > 0:
            print(f"  Skipped line {row['line_number']}: " + "; ".join(problems))
        else:
            valid_rows.append(row)

    usernames = []
    for row in valid_rows:
        username = row["username"].strip()
        if username not in usernames:
            usernames.append(username)
    user_ids = get_user_ids(usernames)

    conversion_time = datetime.now(timezone.utc)
    documents = []
    for row in valid_rows:
        documents.append(convert_row(row, user_ids, conversion_time))

    # Replace all sample-user reviews (also removes reviews from older dataset versions).
    # Reviews made by real users in the app are kept.
    collection = get_reviews_collection()
    removed = collection.delete_many({"user_id": {"$in": get_all_sample_user_ids()}}).deleted_count

    if len(documents) > 0:
        collection.insert_many(documents, ordered=False)

    watched_added = sync_sample_reviews_to_watched_history(documents)

    removed_users = remove_unused_sample_users(usernames)

    print(f"Removed {removed} old sample reviews")
    print(f"Removed {removed_users} unused sample users from older dataset versions")
    print(f"Added {watched_added} imported reviews to watched history")
    print(f"Users in dataset: {len(user_ids)} (created in MariaDB if missing)")
    print(f"Converted and inserted: {len(documents)} reviews | Skipped: {len(rows) - len(valid_rows)}")
    if len(documents) > 0:
        print("Example document:", collection.find_one({"user_id": {"$in": list(user_ids.values())}}, {"_id": 0}))
    print("Review dataset converted successfully!")


if __name__ == "__main__":
    main()
