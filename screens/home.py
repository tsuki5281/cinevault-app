
import streamlit as st

from db.home import get_homepage_data
from db.catalogue import get_all_genres


SEARCH_PAGE_SIZE = 20


@st.cache_data(ttl=300)
def cached_genres():
    return get_all_genres()


def toggle_home_genre(genre):
    selected = list(st.session_state.home_genre_selection)

    if genre in selected:
        selected.remove(genre)
    else:
        selected.append(genre)

    st.session_state.home_genre_selection = selected


def go_to_search_from_genres():
    selected_genres = list(
        st.session_state.get("home_genre_selection", [])
    )

    st.session_state.search_keyword = ""
    st.session_state.search_genres = selected_genres
    st.session_state.search_actors = []
    st.session_state.search_genre_match = "Any"
    st.session_state.search_actor_match = "Any"

    st.session_state.search_filters = {
        "title": None,
        "genres": selected_genres,
        "actors": [],
        "genre_match": "any",
        "actor_match": "any",
        "sort_by": "title_asc"
    }

    st.session_state.search_pending = True
    st.session_state.search_results = None
    st.session_state.search_offset = 0
    st.session_state.search_has_more = False
    st.session_state.curated_visible_count = SEARCH_PAGE_SIZE
    st.session_state.page = "Search"
    st.session_state.navigation_choice = "Search"


def display_movie_collection(
    heading,
    movies,
    collection_type,
    on_movie_select,
    columns_per_row=3
):
    st.subheader(heading)

    if not movies:
        st.info(
            "No movies are available in this collection yet."
        )
        return

    if collection_type == "highest":
        st.caption(
            "Rating guide: Green ≥ 4.0 · Gold 3.0–3.99 · Red below 3.0"
        )

    for start in range(0, len(movies), columns_per_row):
        batch = movies[start:start + columns_per_row]
        columns = st.columns(columns_per_row)

        for index, (column, movie) in enumerate(
            zip(columns, batch)
        ):
            rank = start + index + 1
            movie_id = movie["movie_id"]

            with column:
                with st.container(
                    border=True,
                    key=f"home_movie_{collection_type}_{movie_id}"
                ):
                    st.markdown(
                        f'<div class="cv-card-rank">{rank:02d}</div>',
                        unsafe_allow_html=True
                    )

                    if collection_type == "highest":
                        average = float(movie["average_rating"])
                        rating_count = movie["rating_count"]

                        if average >= 4.0:
                            tier = "HIGHLY RATED"
                            tier_class = "cv-rating-tier-high"
                            score_class = "cv-card-rating-high"
                        elif average >= 3.0:
                            tier = "MIXED RECEPTION"
                            tier_class = "cv-rating-tier-mid"
                            score_class = "cv-card-rating-mid"
                        else:
                            tier = "LOWER RATED"
                            tier_class = "cv-rating-tier-low"
                            score_class = "cv-card-rating-low"

                        st.markdown(
                            f'<div class="cv-rating-tier {tier_class}">'
                            f'{tier}</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f"**{movie['title'] or movie_id}**"
                        )

                        st.markdown(
                            f'<div class="{score_class}">'
                            f'★ {average:.2f}/5'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                        st.caption(
                            f"{rating_count} member ratings"
                        )

                    else:
                        st.markdown(
                            '<div class="cv-card-kicker">'
                            'MOST DISCUSSED'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f"**{movie['title'] or movie_id}**"
                        )

                        st.markdown(
                            f'<div class="cv-card-review-count">'
                            f"{movie['review_count']} reviews"
                            f'</div>',
                            unsafe_allow_html=True
                        )

                        spoiler_count = movie["spoiler_count"]

                        if spoiler_count > 0:
                            spoiler_label = (
                                "⚠ SPOILERS IN "
                                f"{spoiler_count} "
                                f"{'REVIEW' if spoiler_count == 1 else 'REVIEWS'}"
                            )

                            st.markdown(
                                f'<div class="cv-spoiler-alert">'
                                f'{spoiler_label}'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                '<div class="cv-spoiler-safe">'
                                'NO SPOILER REVIEWS'
                                '</div>',
                                unsafe_allow_html=True
                            )

                        st.markdown(
                            '<div style="height: 10px;"></div>',
                            unsafe_allow_html=True
                        )

                    st.button(
                        "View movie",
                        key=f"home_{collection_type}_{movie_id}",
                        use_container_width=True,
                        on_click=on_movie_select,
                        args=(movie_id, "Home")
                    )


def home_page(on_movie_select):
    st.markdown(
        '<div class="cv-eyebrow">YOUR MOVIE COMMUNITY</div>',
        unsafe_allow_html=True
    )

    st.title("Discover movies worth talking about.")

    st.write(
        "Explore community favourites, discover new genres "
        "and find your next movie."
    )

    try:
        homepage = get_homepage_data(
            highest_rated_limit=6,
            most_reviewed_limit=10
        )

    except Exception:
        st.error(
            "Unable to load the Home page. "
            "Please check the database connections."
        )
        return

    featured = homepage["featured_movie"]

    st.divider()
    st.subheader("Featured Movie")

    if featured:
        with st.container(key="featured_hero"):
            details_col, rating_col = st.columns(
                [3, 1],
                gap="large",
                vertical_alignment="center"
            )

            with details_col:
                st.markdown(
                    '<div class="cv-hero-label">'
                    'CINEVAULT COMMUNITY PICK'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.title(featured["title"])

                description = featured.get("description") or (
                    "Discover this movie in the CineVault catalogue."
                )

                if len(description) > 350:
                    description = (
                        description[:350].rsplit(" ", 1)[0] + "..."
                    )

                st.write(description)

                if featured["genres"]:
                    st.markdown(
                        '<div class="cv-genre-caption">'
                        + "  ·  ".join(featured["genres"])
                        + '</div>',
                        unsafe_allow_html=True
                    )

                st.write("")

                st.button(
                    "Explore this movie",
                    key="featured_movie_button",
                    type="primary",
                    on_click=on_movie_select,
                    args=(featured["movie_id"], "Home")
                )

            with rating_col:
                st.metric(
                    "Community rating",
                    f"{float(featured['average_rating']):.2f}/5"
                )

                st.caption(
                    f"Based on {featured['rating_count']} member ratings"
                )

    else:
        st.info(
            "No featured movie is available yet. "
            "Explore the catalogue to discover movies."
        )

    st.divider()

    display_movie_collection(
        "Highest-Rated Movies",
        homepage["highest_rated"],
        "highest",
        on_movie_select,
        columns_per_row=3
    )

    st.divider()

    display_movie_collection(
        "Most-Reviewed Movies",
        homepage["most_reviewed"],
        "reviewed",
        on_movie_select,
        columns_per_row=5
    )

    st.divider()

    st.markdown(
        '<div class="cv-eyebrow">FIND YOUR NEXT FAVOURITE</div>',
        unsafe_allow_html=True
    )

    st.subheader("Explore by Genre")

    st.caption(
        "Choose one or more genres to discover movies "
        "that match your interests."
    )

    genre_names = [
        genre["genre_name"]
        for genre in cached_genres()
    ]

    selected_genres = st.session_state.home_genre_selection

    genre_columns = st.columns(5)

    for index, genre in enumerate(genre_names):
        selected = genre in selected_genres

        with genre_columns[index % 5]:
            st.button(
                f"✓  {genre}" if selected else genre,
                key=f"home_genre_{genre}",
                type="primary" if selected else "secondary",
                use_container_width=True,
                on_click=toggle_home_genre,
                args=(genre,)
            )

    st.write("")

    if selected_genres:
        st.caption(
            "Selected: " + " · ".join(selected_genres)
        )

    st.button(
        "Explore Selected Genres",
        type="primary",
        disabled=not selected_genres,
        on_click=go_to_search_from_genres
    )
