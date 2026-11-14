
from db.authentication import get_demo_users
from db.mariadb import add_to_watchlist, mark_as_watched


PROFILE_USERNAME = "sample_user_07"

WATCHED_MOVIES = [
    "s101",  # 3 Idiots
    "s28",   # #Alive
    "s107"   # 365 Days
]

WATCHLIST_MOVIES = [
    "s122",  # 50 First Dates
    "s128",  # 6 Underground
    "s10"    # 1920
]


def main():
    demo_users = {
        user["username"]: user
        for user in get_demo_users()
    }

    if PROFILE_USERNAME not in demo_users:
        raise ValueError(
            f"Demo account {PROFILE_USERNAME} was not found."
        )

    user_id = demo_users[PROFILE_USERNAME]["user_id"]

    print(f"Seeding activity for {PROFILE_USERNAME}...")

    for movie_id in WATCHED_MOVIES:
        added = mark_as_watched(user_id, movie_id)
        status = "Added" if added else "Already exists"
        print(f"Watched {movie_id}: {status}")

    for movie_id in WATCHLIST_MOVIES:
        added = add_to_watchlist(user_id, movie_id)
        status = "Added" if added else "Already exists"
        print(f"Watchlist {movie_id}: {status}")

    print("Demo activity setup complete.")


if __name__ == "__main__":
    main()
