from db.catalogue import browse_movies, get_movie_details


def run_tests():
    # 1. Movie details
    movie = get_movie_details("s10")
    assert movie is not None
    assert movie["title"] == "1920"
    assert "Horror Movies" in movie["genres"]
    assert "Rajneesh Duggal" in movie["actors"]

    # 2. Non-existent movie
    assert get_movie_details("nonexistent") is None

    # 3. No-match searches
    assert browse_movies(title="xyz123nonexistent") == []
    assert browse_movies(genres=["Nonexistent Genre"]) == []
    assert browse_movies(actors=["Nonexistent Actor"]) == []

    # 4. Sorting
    ascending = browse_movies(limit=100)
    descending = browse_movies(sort_by="title_desc", limit=100)

    assert len(ascending) == 100
    assert len(descending) == 100

    # Check that both sorting options return the correct first page
    ascending_again = browse_movies(
        sort_by="title_asc",
        limit=100
    )

    descending_again = browse_movies(
        sort_by="title_desc",
        limit=100
    )

    assert ascending == ascending_again
    assert descending == descending_again

    print("PASS: Sorting queries return consistent results")

    # Compare the first and last pages in opposite sort directions
    total_movies = 4677

    first_asc = browse_movies(
        sort_by="title_asc",
        limit=5
    )

    last_desc = browse_movies(
        sort_by="title_desc",
        limit=5,
        offset=total_movies - 5
    )

    assert (
        [m["title"] for m in first_asc]
        ==
        [m["title"] for m in reversed(last_desc)]
    )

    print("PASS: Ascending and descending sorting are consistent")

    # 5. Pagination
    page1 = browse_movies(limit=5, offset=0)
    page2 = browse_movies(limit=5, offset=5)
    assert len(page1) == 5
    assert len(page2) == 5
    assert not (
        {m["movie_id"] for m in page1}
        & {m["movie_id"] for m in page2}
    )

    # 6. Combined filtering
    results = browse_movies(
        genres=["Horror Movies", "Thrillers"],
        actors=["Rajneesh Duggal", "Adah Sharma"],
        genre_match="all",
        actor_match="all"
    )

    assert len(results) >= 1

    for result in results:
        details = get_movie_details(result["movie_id"])
        assert all(
            g in details["genres"]
            for g in ["Horror Movies", "Thrillers"]
        )
        assert all(
            a in details["actors"]
            for a in ["Rajneesh Duggal", "Adah Sharma"]
        )

    # Verify AND/OR genre and actor filtering against the full catalogue
    # Retrieve all movies using pagination
    all_movies = []

    for offset in range(0, 4677, 100):
        all_movies.extend(browse_movies(limit=100, offset=offset))

    print(f"Loaded {len(all_movies)} movie IDs", flush=True)

    # Cache the movie details
    movie_details = {}

    for index, movie in enumerate(all_movies, start=1):
        movie_details[movie["movie_id"]] = get_movie_details(movie["movie_id"])

        if index % 500 == 0:
            print(f"Loaded {index} movie details", flush=True)

    print("Finished loading movie details!", flush=True)

    test_cases = [
        {
            "genres": ["Horror Movies", "Thrillers"],
            "genre_match": "all"
        },
        {
            "genres": ["Horror Movies", "Thrillers"],
            "genre_match": "any"
        },
        {
            "actors": ["Rajneesh Duggal", "Adah Sharma"],
            "actor_match": "all"
        },
        {
            "actors": ["Rajneesh Duggal", "Adah Sharma"],
            "actor_match": "any"
        },
        {
            "genres": ["Horror Movies", "Thrillers"],
            "actors": ["Rajneesh Duggal", "Adah Sharma"],
            "genre_match": "all",
            "actor_match": "all"
        }
    ]

    for filters in test_cases:
        actual = []

        for offset in range(0, 4677, 100):
            actual.extend(browse_movies(**filters, limit=100, offset=offset))

        expected = []

        for movie in all_movies:
            details = movie_details[movie["movie_id"]]

            genre_tags = details["genres"]
            actor_tags = details["actors"]

            selected_genres = filters.get("genres", [])
            selected_actors = filters.get("actors", [])

            genre_match = filters.get("genre_match", "all")
            actor_match = filters.get("actor_match", "all")

            genre_ok = (
                not selected_genres
                or (
                    all(g in genre_tags for g in selected_genres)
                    if genre_match == "all"
                    else any(g in genre_tags for g in selected_genres)
                )
            )

            actor_ok = (
                not selected_actors
                or (
                    all(a in actor_tags for a in selected_actors)
                    if actor_match == "all"
                    else any(a in actor_tags for a in selected_actors)
                )
            )

            if genre_ok and actor_ok:
                expected.append(movie["movie_id"])

        assert {m["movie_id"] for m in actual} == set(expected), (
            f"Filter mismatch: {filters}"
        )

        print(f"PASS: {filters} -> {len(actual)} matching movies")

    print("PASS: Catalogue tests completed successfully!")


if __name__ == "__main__":
    run_tests()