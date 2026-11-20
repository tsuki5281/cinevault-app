
import html
import streamlit as st

from db.catalogue import (
    browse_movies,
    get_all_genres,
    get_movie_card_details,
    get_recommended_actors,
    get_search_suggestions,
)
from db.mariadb import (
    get_highest_rated_movies,
    get_movie_rating_summaries,
    get_movies_sorted_by_rating,
)
from db.mongodb import get_most_reviewed_movies


SEARCH_PAGE_SIZE = 20


@st.cache_data(ttl=120)
def cached_search_suggestions(keyword):
    return get_search_suggestions(keyword, limit=5)


@st.cache_data(ttl=300)
def cached_genres():
    return get_all_genres()


@st.cache_data(ttl=300)
def cached_recommended_actors():
    return get_recommended_actors(limit=12)


@st.cache_data(ttl=120)
def get_curated_search_movies():
    most_reviewed = get_most_reviewed_movies(limit=50)

    highest_rated = get_highest_rated_movies(
        minimum_ratings=2,
        limit=50
    )

    selected = []
    seen = set()

    for movie in most_reviewed + highest_rated:
        movie_id = movie["movie_id"]

        if movie_id not in seen:
            selected.append(movie)
            seen.add(movie_id)

    return build_movie_cards(selected)


def build_movie_cards(movies):
    if not movies:
        return []

    movie_ids = [
        movie["movie_id"]
        for movie in movies
    ]

    details = get_movie_card_details(movie_ids)
    rating_summaries = get_movie_rating_summaries(movie_ids)

    results = []

    for movie in movies:
        movie_id = movie["movie_id"]
        metadata = details.get(movie_id)

        if metadata is None:
            continue

        rating = rating_summaries.get(
            movie_id,
            {"average_rating": None, "rating_count": 0}
        )

        results.append({
            "movie_id": movie_id,
            "title": metadata["title"],
            "genres": metadata["genres"],
            "average_rating": rating["average_rating"],
            "rating_count": rating["rating_count"],
            "review_count": movie.get("review_count", 0),
            "spoiler_count": movie.get("spoiler_count", 0)
        })

    return results


def retrieve_search_page(filters, offset, ranked_movies=None):
    search_arguments = {
        "title": filters["title"],
        "genres": filters["genres"],
        "actors": filters["actors"],
        "genre_match": filters["genre_match"],
        "actor_match": filters["actor_match"]
    }

    if filters["sort_by"] == "rating_desc":
        if ranked_movies is None:
            matching_movies = browse_movies(
                **search_arguments,
                sort_by="title_asc",
                limit=None,
                offset=0
            )

            ranked_movies = get_movies_sorted_by_rating(
                [movie["movie_id"] for movie in matching_movies]
            )

        page_with_extra = ranked_movies[
            offset:offset + SEARCH_PAGE_SIZE + 1
        ]
        has_more = len(page_with_extra) > SEARCH_PAGE_SIZE
        page_movies = page_with_extra[:SEARCH_PAGE_SIZE]

    else:
        movies = browse_movies(
            **search_arguments,
            sort_by=filters["sort_by"],
            limit=SEARCH_PAGE_SIZE + 1,
            offset=offset
        )

        has_more = len(movies) > SEARCH_PAGE_SIZE
        page_movies = movies[:SEARCH_PAGE_SIZE]

    cards = build_movie_cards(page_movies)

    return cards, has_more, len(page_movies), ranked_movies


def perform_search(filters):
    try:
        with st.spinner("Searching the CineVault catalogue..."):
            cards, has_more, fetched_count, ranked_movies = retrieve_search_page(
                filters,
                offset=0
            )

        st.session_state.search_filters = filters
        st.session_state.search_results = cards
        st.session_state.search_offset = fetched_count
        st.session_state.search_has_more = has_more
        st.session_state.search_ranked_movies = ranked_movies

    except ValueError as error:
        st.warning(str(error))

    except Exception as error:
        st.error("Unable to retrieve search results.")
        st.exception(error)


def open_movie_details(movie_id, source_page):
    st.session_state.selected_movie_id = movie_id
    st.session_state.previous_page = source_page
    st.session_state.navigation_choice = source_page
    st.session_state.page = "Movie Details"
    st.session_state.scroll_to_top_on_details = True


def toggle_search_actor(actor):
    selected = list(st.session_state.search_actors)

    if actor in selected:
        selected.remove(actor)
    else:
        selected.append(actor)

    st.session_state.search_actors = selected

    # Clear the suggestion keyword so it cannot become a title filter.
    st.session_state.search_keyword = ""


def toggle_search_genre(genre):
    selected = list(st.session_state.search_genres)

    if genre in selected:
        selected.remove(genre)
    else:
        selected.append(genre)

    st.session_state.search_genres = selected

    # Clear the suggestion keyword so it cannot become a title filter.
    st.session_state.search_keyword = ""


def display_search_suggestions(keyword):
    if len(keyword.strip()) < 2:
        return

    try:
        suggestions = cached_search_suggestions(keyword.strip())

    except Exception as error:
        st.error("Unable to retrieve search suggestions.")
        st.exception(error)
        return

    if not any(suggestions.values()):
        st.caption("No matching suggestions found.")
        return

    st.markdown(
        '<div class="cv-eyebrow">QUICK SUGGESTIONS</div>',
        unsafe_allow_html=True
    )

    movie_col, actor_col, genre_col = st.columns(3)

    with movie_col:
        st.markdown("**Movies**")

        if suggestions["movies"]:
            for movie in suggestions["movies"]:
                st.button(
                    movie["title"],
                    key=f"suggest_movie_{movie['movie_id']}",
                    use_container_width=True,
                    on_click=open_movie_details,
                    args=(movie["movie_id"], "Search")
                )
        else:
            st.caption("No matching movies.")

    with actor_col:
        st.markdown("**Actors**")

        if suggestions["actors"]:
            for actor in suggestions["actors"]:
                actor_name = actor["actor_name"]
                selected = actor_name in st.session_state.search_actors

                st.button(
                    ("✓ " if selected else "+ ") + actor_name,
                    key=f"suggest_actor_{actor['actor_id']}",
                    type="primary" if selected else "secondary",
                    use_container_width=True,
                    on_click=toggle_search_actor,
                    args=(actor_name,)
                )
        else:
            st.caption("No matching actors.")

    with genre_col:
        st.markdown("**Genres**")

        if suggestions["genres"]:
            for genre in suggestions["genres"]:
                genre_name = genre["genre_name"]
                selected = genre_name in st.session_state.search_genres

                st.button(
                    ("✓ " if selected else "+ ") + genre_name,
                    key=f"suggest_genre_{genre['genre_id']}",
                    type="primary" if selected else "secondary",
                    use_container_width=True,
                    on_click=toggle_search_genre,
                    args=(genre_name,)
                )
        else:
            st.caption("No matching genres.")


def display_demo_actor_chips():
    st.markdown("**Quick picks from demo cast**")

    st.caption(
        "Select actors featured in our curated demo movies."
    )

    try:
        actors = cached_recommended_actors()

    except Exception as error:
        st.error("Unable to load demo cast suggestions.")
        st.exception(error)
        return

    if not actors:
        st.caption("No demo cast suggestions are available.")
        return

    columns = st.columns(4)

    for index, actor in enumerate(actors):
        actor_name = actor["actor_name"]
        selected = actor_name in st.session_state.search_actors

        with columns[index % 4]:
            st.button(
                ("✓ " if selected else "+ ") + actor_name,
                key=f"demo_actor_{actor['actor_id']}",
                type="primary" if selected else "secondary",
                use_container_width=True,
                on_click=toggle_search_actor,
                args=(actor_name,)
            )


def display_search_genre_chips():
    try:
        genre_names = [
            genre["genre_name"]
            for genre in cached_genres()
        ]

    except Exception as error:
        st.error("Unable to load genres.")
        st.exception(error)
        return

    st.markdown("**Genres**")
    st.caption("Select one or more genres to narrow your search.")

    selected_genres = st.session_state.search_genres
    columns = st.columns(5)

    for index, genre in enumerate(genre_names):
        selected = genre in selected_genres

        with columns[index % 5]:
            st.button(
                f"✓  {genre}" if selected else genre,
                key=f"search_genre_chip_{genre}",
                type="primary" if selected else "secondary",
                use_container_width=True,
                on_click=toggle_search_genre,
                args=(genre,)
            )

    if selected_genres:
        st.caption(
            "Selected genres: " + " · ".join(selected_genres)
        )


def display_selected_actors():
    selected_actors = st.session_state.search_actors

    if not selected_actors:
        return

    st.markdown("**Selected actors**")

    columns = st.columns(min(4, len(selected_actors)))

    for index, actor in enumerate(list(selected_actors)):
        with columns[index % len(columns)]:
            st.button(
                f"✕ {actor}",
                key=f"remove_search_actor_{index}",
                on_click=toggle_search_actor,
                args=(actor,)
            )


def display_search_results(results, heading):
    st.subheader(heading)

    if not results:
        st.info(
            "No movies matched your search. "
            "Try changing your filters."
        )
        return

    st.caption(f"{len(results)} movies displayed")

    for start in range(0, len(results), 4):
        batch = results[start:start + 4]
        columns = st.columns(4)

        for column, movie in zip(columns, batch):
            movie_id = movie["movie_id"]

            with column:
                with st.container(
                    border=True,
                    key=f"search_movie_card_{movie_id}"
                ):
                    st.caption("CINEVAULT COLLECTION")

                    title = html.escape(
                        str(movie.get("title") or movie_id)
                    )

                    genres = html.escape(
                        str(
                            movie.get("genres")
                            or "Genre information unavailable"
                        )
                    )

                    st.markdown(
                        f'<div class="cv-search-title">'
                        f'{title}</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f'<div class="cv-search-genres">'
                        f'{genres}</div>',
                        unsafe_allow_html=True
                    )

                    average = movie.get("average_rating")

                    if average is not None:
                        average = float(average)

                        if average >= 4.0:
                            score_class = "cv-card-rating-high"
                        elif average >= 3.0:
                            score_class = "cv-card-rating-mid"
                        else:
                            score_class = "cv-card-rating-low"

                        rating_html = (
                            '<div class="cv-search-rating-slot">'
                            f'<div class="{score_class}">'
                            f'★ {average:.2f}/5'
                            '</div>'
                            '<div class="cv-search-rating-count">'
                            f"{movie['rating_count']} member ratings"
                            '</div>'
                            '</div>'
                        )

                    else:
                        rating_html = (
                            '<div class="cv-search-rating-slot">'
                            '<div class="cv-search-not-rated">'
                            'NOT RATED YET'
                            '</div>'
                            '<div class="cv-search-rating-count">'
                            'No community ratings'
                            '</div>'
                            '</div>'
                        )

                    st.markdown(
                        rating_html,
                        unsafe_allow_html=True
                    )

                    st.button(
                        "View details",
                        key=f"search_view_{movie_id}",
                        use_container_width=True,
                        on_click=open_movie_details,
                        args=(movie_id, "Search")
                    )


def clear_search_filters():
    st.session_state.search_keyword = ""
    st.session_state.search_genres = []
    st.session_state.search_actors = []
    st.session_state.search_genre_match = "Any"
    st.session_state.search_actor_match = "Any"
    st.session_state.search_sort = "Title A–Z"
    st.session_state.search_filters = None
    st.session_state.search_results = None
    st.session_state.search_offset = 0
    st.session_state.search_has_more = False
    st.session_state.search_pending = False
    st.session_state.search_ranked_movies = None
    st.session_state.curated_visible_count = SEARCH_PAGE_SIZE


def load_more_curated_results():
    st.session_state.curated_visible_count += SEARCH_PAGE_SIZE


def load_more_search_results():
    filters = st.session_state.search_filters
    offset = st.session_state.search_offset

    try:
        cards, has_more, fetched_count, ranked_movies = retrieve_search_page(
            filters,
            offset,
            ranked_movies=st.session_state.search_ranked_movies
        )

        st.session_state.search_results.extend(cards)
        st.session_state.search_offset += fetched_count
        st.session_state.search_has_more = has_more
        st.session_state.search_ranked_movies = ranked_movies

    except Exception as error:
        st.error("Unable to load more movies.")
        st.exception(error)


def initialise_search_state():
    defaults = {
        "search_filters": None,
        "search_keyword": "",
        "search_genres": [],
        "search_actors": [],
        "search_genre_match": "Any",
        "search_actor_match": "Any",
        "search_sort": "Title A–Z",
        "search_results": None,
        "search_offset": 0,
        "search_has_more": False,
        "search_pending": False,
        "search_ranked_movies": None,
        "curated_visible_count": SEARCH_PAGE_SIZE
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def search_page(_open_movie_details=None):
    initialise_search_state()

    st.markdown(
        '<div class="cv-eyebrow">THE COLLECTION</div>',
        unsafe_allow_html=True
    )

    st.title("Find your next movie.")

    st.caption(
        "Search across movie titles, actors and genres, "
        "or explore community recommendations."
    )

    if st.session_state.search_pending:
        filters = st.session_state.search_filters
        st.session_state.search_pending = False

        if filters is not None:
            perform_search(filters)

    st.divider()

    st.subheader("Universal Search")

    keyword = st.text_input(
        "Search movies, actors or genres",
        placeholder="Try a movie title, actor name or genre...",
        key="search_keyword"
    )

    display_search_suggestions(keyword)

    st.divider()

    st.subheader("Refine Your Search")

    with st.container(border=True):
        display_search_genre_chips()

        if st.session_state.search_genres:
            st.divider()

            st.markdown("**Genre Matching**")

            st.radio(
                "Genre matching",
                ["Any", "All"],
                horizontal=True,
                key="search_genre_match",
                label_visibility="collapsed"
            )

        else:
            st.session_state.search_genre_match = "Any"

        st.divider()

        display_demo_actor_chips()

        display_selected_actors()

        if st.session_state.search_actors:
            st.divider()

            st.markdown("**Actor Matching**")

            st.radio(
                "Actor matching",
                ["Any", "All"],
                horizontal=True,
                key="search_actor_match",
                label_visibility="collapsed"
            )

        else:
            st.session_state.search_actor_match = "Any"

    st.divider()

    st.selectbox(
        "Sort results",
        ["Title A–Z", "Highest rated"],
        key="search_sort"
    )

    search_col, clear_col = st.columns(2)

    with search_col:
        search_clicked = st.button(
            "Search Catalogue",
            type="primary",
            use_container_width=True
        )

    with clear_col:
        st.button(
            "Clear Filters",
            use_container_width=True,
            on_click=clear_search_filters
        )

    if search_clicked:
        filters = {
            "title": keyword.strip() or None,
            "genres": list(st.session_state.search_genres),
            "actors": list(st.session_state.search_actors),
            "genre_match": (
                "all"
                if st.session_state.search_genre_match == "All"
                else "any"
            ),
            "actor_match": (
                "all"
                if st.session_state.search_actor_match == "All"
                else "any"
            ),
            "sort_by": (
                "rating_desc"
                if st.session_state.search_sort == "Highest rated"
                else "title_asc"
            )
        }

        if (
            not filters["title"]
            and not filters["genres"]
            and not filters["actors"]
        ):
            st.warning(
                "Enter a search term or select at least one filter."
            )

        else:
            st.session_state.curated_visible_count = SEARCH_PAGE_SIZE
            perform_search(filters)

    st.divider()

    if st.session_state.search_filters is None:
        st.markdown(
            '<div class="cv-eyebrow">COMMUNITY PICKS</div>',
            unsafe_allow_html=True
        )

        st.subheader("Popular in CineVault")

        st.caption(
            "A selection of community favourites to get you started."
        )

        try:
            curated_movies = get_curated_search_movies()
            visible_count = st.session_state.curated_visible_count

            display_search_results(
                curated_movies[:visible_count],
                "Recommended Movies"
            )

            if len(curated_movies) > visible_count:
                st.caption(
                    f"Showing {min(visible_count, len(curated_movies))} "
                    f"of {len(curated_movies)} recommendations."
                )

                st.button(
                    "Load More Movies",
                    key="load_more_curated",
                    type="primary",
                    use_container_width=True,
                    on_click=load_more_curated_results
                )

            else:
                st.caption(
                    "You've reached the end of the recommendations."
                )

        except Exception as error:
            st.error("Unable to load curated movie recommendations.")
            st.exception(error)

    elif st.session_state.search_results is not None:
        display_search_results(
            st.session_state.search_results,
            "Search Results"
        )

        if st.session_state.search_has_more:
            st.button(
                "Load More Movies",
                key="load_more_search",
                type="primary",
                use_container_width=True,
                on_click=load_more_search_results
            )

        elif st.session_state.search_results:
            st.caption("You've reached the end of the search results.")
