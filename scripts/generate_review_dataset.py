# Creates the sample review dataset: data/reviews.csv
# Netflix does not publish user reviews, so the reviews are generated (allowed by the project FAQ).
# The dataset is created independently of MongoDB; scripts/convert_reviews_to_mongo.py loads it.
#
# Run from the repository root:
#   python -m scripts.generate_review_dataset
#
# random.seed(42) means the same CSV is produced every time.

import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MOVIES_CSV = BASE_DIR / "data" / "netflix_movies_cleaned.csv"
REVIEWS_CSV = BASE_DIR / "data" / "reviews.csv"

NUM_USERS = 200
REVIEWS_PER_USER = 100         # 200 x 100 = 20,000 reviews (about 4 per movie)
USERNAME_PREFIX = "sample_user_"

random.seed(42)

openings = ["Honestly,", "I watched this over the weekend and", "Not gonna lie,",
            "Watched it with friends and", "After all the hype,", "Surprisingly,"]
good = ["it was really enjoyable", "the acting was excellent", "the story kept me hooked",
        "the visuals were stunning", "it was worth every minute", "the soundtrack was great"]
bad = ["it was quite slow", "the ending felt rushed", "the plot was predictable",
       "the dialogue felt forced", "it dragged in the middle", "it didn't live up to the hype"]
closings = ["Would recommend.", "Would watch again.", "Probably skip this one.",
            "Good for a lazy night.", "Solid overall.", "Not my cup of tea."]
spoiler_lines = ["The twist at the end changes everything.",
                 "I didn't expect the main character to die.",
                 "The villain turns out to be the mentor."]
tag_pool = ["acting", "story", "visuals", "ending", "soundtrack", "slow", "funny",
            "emotional", "rewatchable", "overrated", "family", "scary"]

START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 11, 1, tzinfo=timezone.utc)


# Reads movie_id and the first genre of every movie in the cleaned catalogue
def read_movies():
    movies = []
    with open(MOVIES_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            first_genre = ""
            if row["genre"]:
                first_genre = row["genre"].split(",")[0].strip()
            movies.append({"movie_id": row["movie_id"], "genre": first_genre})
    return movies


def make_review(username, movie):
    if random.random() < 0.6:
        middle = random.choice(good)
    else:
        middle = random.choice(bad)

    genre_text = "this movie"
    if movie["genre"]:
        genre_text = "this " + movie["genre"].lower() + " pick"

    text = random.choice(openings) + " " + genre_text + " was one where " + middle + \
        ". " + random.choice(closings)

    spoiler = random.random() < 0.15
    if spoiler:
        text = text + " " + random.choice(spoiler_lines)

    tags = random.sample(tag_pool, random.randint(0, 3))

    days = (END_DATE - START_DATE).days
    created_at = START_DATE + timedelta(days=random.randint(0, days),
                                        minutes=random.randint(0, 1439))

    return {
        "username": username,
        "movie_id": movie["movie_id"],
        "review_text": text,
        "spoiler": str(spoiler),                 # "True" / "False"
        "tags": ";".join(tags),                  # e.g. "acting;ending"
        "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main():
    movies = read_movies()

    # random.sample picks different movies, so no user reviews the same movie twice
    rows = []
    for i in range(1, NUM_USERS + 1):
        username = USERNAME_PREFIX + str(i).zfill(2)
        for movie in random.sample(movies, REVIEWS_PER_USER):
            rows.append(make_review(username, movie))

    fields = ["username", "movie_id", "review_text", "spoiler", "tags", "created_at"]
    with open(REVIEWS_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Read {len(movies)} movies from {MOVIES_CSV.name}")
    print(f"Wrote {len(rows)} reviews to data/{REVIEWS_CSV.name}")


if __name__ == "__main__":
    main()
