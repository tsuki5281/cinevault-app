# Conversion script: data/reviews.csv -> MongoDB "reviews" documents
#
# The CSV is flat text. Each row is converted into a typed MongoDB document:
#   username "sample_user_01"   -> user_id 1        (looked up / created in MariaDB users table)
#   spoiler  "True"             -> True             (bool)
#   tags     "acting;ending"    -> ["acting", "ending"]  (array)
#   created_at "2026-03-01T..." -> datetime         (BSON date)
# Rows whose movie_id is not in the MariaDB movies table are skipped and reported.
#
# Run from the repository root (after scripts.import_movies and scripts.init_mongodb):
#   python -m scripts.convert_reviews_to_mongo

import csv
from datetime import datetime, timezone
from pathlib import Path

from db.mariadb import get_connection
from db.mongodb import get_reviews_collection, setup_reviews_collection

BASE_DIR = Path(__file__).resolve().parent.parent
REVIEWS_CSV = BASE_DIR / "data" / "reviews.csv"


def read_csv_rows():
    rows = []
    with open(REVIEWS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


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


# Converts one CSV row (all strings) into a typed review document
def convert_row(row, user_ids):
    tags = []
    for tag in row["tags"].split(";"):
        tag = tag.strip().lower()
        if tag != "" and tag not in tags:
            tags.append(tag)

    created_at = datetime.strptime(row["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    created_at = created_at.replace(tzinfo=timezone.utc)

    return {
        "user_id": user_ids[row["username"]],
        "movie_id": row["movie_id"],
        "review_text": row["review_text"].strip(),
        "spoiler": row["spoiler"] == "True",
        "tags": tags,
        "created_at": created_at,
    }


def main():
    setup_reviews_collection()

    rows = read_csv_rows()
    print(f"Read {len(rows)} rows from data/{REVIEWS_CSV.name}")

    usernames = []
    for row in rows:
        if row["username"] not in usernames:
            usernames.append(row["username"])
    user_ids = get_user_ids(usernames)
    movie_ids = get_movie_ids()

    documents = []
    skipped = 0
    for row in rows:
        if row["movie_id"] not in movie_ids or row["review_text"].strip() == "":
            skipped = skipped + 1
            continue
        documents.append(convert_row(row, user_ids))

    # Replace only the dataset users' reviews, so reviews made in the app are kept
    collection = get_reviews_collection()
    sample_user_ids = []
    for username in user_ids:
        sample_user_ids.append(user_ids[username])
    collection.delete_many({"user_id": {"$in": sample_user_ids}})

    if len(documents) > 0:
        collection.insert_many(documents, ordered=False)

    print(f"Users in dataset: {len(user_ids)} (created in MariaDB if missing)")
    print(f"Converted and inserted: {len(documents)} reviews | Skipped: {skipped}")
    print("Example document:", collection.find_one({}, {"_id": 0}))
    print("Review dataset converted successfully!")


if __name__ == "__main__":
    main()
