# Performance analysis for the MongoDB part. Screenshot the output for the report.
#
# Test 1: reviews for one movie, with no index (COLLSCAN) vs the movie_newest index.
# Test 2: SQL vs NoSQL - find all movies in a genre:
#         MariaDB (3-table JOIN) vs MongoDB (embedded genres array, multikey index).
#
# Run from the repository root (after convert_reviews_to_mongo and convert_movies_to_mongo):
#   python -m scripts.performance_mongodb

import time

from db.mariadb import get_connection
from db.mongodb import get_mongo_db

RUNS = 200


# Collects stage names from an explain plan, e.g. ["FETCH", "IXSCAN"]
def plan_stages(plan):
    names = []
    if isinstance(plan, dict):
        if "stage" in plan:
            names.append(plan["stage"])
        for value in plan.values():
            names = names + plan_stages(value)
    elif isinstance(plan, list):
        for item in plan:
            names = names + plan_stages(item)
    return names


def average_ms(function):
    start = time.perf_counter()
    for _ in range(RUNS):
        function()
    return (time.perf_counter() - start) / RUNS * 1000


def test_review_index(db):
    reviews = db["reviews"]

    top = list(reviews.aggregate([
        {"$group": {"_id": "$movie_id", "n": {"$sum": 1}}},
        {"$sort": {"n": -1}}, {"$limit": 1}]))
    movie_id = top[0]["_id"]
    query = {"movie_id": movie_id}

    print(f"TEST 1: reviews for movie {movie_id}, newest first "
          f"({reviews.count_documents({})} reviews in collection)")
    print("%-22s %-24s %9s %13s %13s %9s" %
          ("Method", "Plan", "Returned", "DocsExamined", "KeysExamined", "Avg ms"))

    tests = [("No index (COLLSCAN)", {"$natural": 1}), ("movie_newest index", "movie_newest")]
    results = []
    for label, hint in tests:
        explain = db.command(
            "explain",
            {"find": "reviews", "filter": query, "sort": {"created_at": -1}, "hint": hint},
            verbosity="executionStats")
        stats = explain["executionStats"]
        stages = " > ".join(plan_stages(explain["queryPlanner"]["winningPlan"]))

        def run_query():
            list(reviews.find(query).sort("created_at", -1).hint(hint))

        ms = average_ms(run_query)
        results.append(ms)
        print("%-22s %-24s %9d %13d %13d %9.3f" %
              (label, stages, stats["nReturned"], stats["totalDocsExamined"],
               stats["totalKeysExamined"], ms))

    if results[1] > 0:
        print(f"-> The index is about {results[0] / results[1]:.1f}x faster\n")


def test_sql_vs_nosql(db, genre="Dramas"):
    print(f"TEST 2: all movies in genre '{genre}' (SQL JOIN vs MongoDB embedded array)")

    sql = """
        SELECT m.movie_id, m.title
        FROM movies AS m
        JOIN movie_genres AS mg ON m.movie_id = mg.movie_id
        JOIN genres AS g ON mg.genre_id = g.genre_id
        WHERE g.genre_name = %s
    """
    connection = get_connection()

    try:
        def run_sql():
            with connection.cursor() as cursor:
                cursor.execute(sql, (genre,))
                return cursor.fetchall()

        sql_count = len(run_sql())
        sql_ms = average_ms(run_sql)

    finally:
        connection.close()

    movies = db["movies"]

    def run_mongo():
        return list(movies.find({"genres": genre}, {"_id": 0, "movie_id": 1, "title": 1}))

    mongo_count = len(run_mongo())
    mongo_ms = average_ms(run_mongo)

    print("%-34s %9s %9s" % ("Method", "Returned", "Avg ms"))
    print("%-34s %9d %9.3f" % ("MariaDB: 3-table JOIN", sql_count, sql_ms))
    print("%-34s %9d %9.3f" % ("MongoDB: genres array + index", mongo_count, mongo_ms))
    if sql_count != mongo_count:
        print("WARNING: result counts differ - rerun scripts.convert_movies_to_mongo")
    print("Note: both databases run locally, so the times include Python driver overhead.")


def main():
    db = get_mongo_db()
    test_review_index(db)
    test_sql_vs_nosql(db)


if __name__ == "__main__":
    main()
