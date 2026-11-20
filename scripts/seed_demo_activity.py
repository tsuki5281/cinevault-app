"""
Seed different watched-history and watchlist entries
for CineVault's three featured demo profiles.

Safe to run repeatedly:
- Existing watched-history entries are preserved.
- Existing watchlist entries are preserved.
- Duplicate entries are skipped.
"""

from db.authentication import get_demo_users
from db.mariadb import add_to_watchlist, mark_as_watched


# Different activity for each featured demo profile.
DEMO_ACTIVITY = {
    "sample_user_06": {
        # Movies this profile has already reviewed.
        "watched": ["s101", "s28", "s107", "s122"],

        # Movies saved for later.
        "watchlist": ["s128", "s10"]
    },

    "sample_user_07": {
        "watched": ["s4", "s23", "s32"],
        "watchlist": ["s122", "s128", "s10"]
    },

    "sample_user_11": {
        "watched": ["s4", "s28", "s101"],
        "watchlist": ["s107", "s122", "s128", "s10"]
    }
}


def main():

    # Retrieve available demo accounts.
    demo_users = {
        user["username"]: user
        for user in get_demo_users()
    }

    # Check that all three featured profiles exist.
    missing_users = set(DEMO_ACTIVITY) - set(demo_users)

    if missing_users:
        raise ValueError(
            f"Missing demo accounts: {sorted(missing_users)}. "
            "Run the review import script first."
        )

    total_watched = 0
    total_watchlist = 0

    # Seed activity for each featured profile.
    for username, activity in DEMO_ACTIVITY.items():

        user_id = demo_users[username]["user_id"]

        print(f"\nSeeding activity for {username}...")

        # Watched history
        for movie_id in activity["watched"]:

            added = mark_as_watched(user_id, movie_id)

            status = "Added" if added else "Already exists"

            print(f"  Watched {movie_id}: {status}")

            if added:
                total_watched += 1

        # Watchlist
        for movie_id in activity["watchlist"]:

            added = add_to_watchlist(user_id, movie_id)

            status = "Added" if added else "Already exists"

            print(f"  Watchlist {movie_id}: {status}")

            if added:
                total_watchlist += 1

    print("\n================================")
    print("Demo activity setup completed!")
    print("================================")
    print(f"New watched entries: {total_watched}")
    print(f"New watchlist entries: {total_watchlist}")
    print(f"Featured profiles updated: {len(DEMO_ACTIVITY)}")


if __name__ == "__main__":
    main()