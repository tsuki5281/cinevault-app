
import streamlit as st

from db.authentication import get_user_by_id
from db.catalogue import get_movie_details
from db.mariadb import (
    add_rating,
    add_to_watchlist,
    delete_rating,
    get_average_rating,
    get_rating,
    get_rating_count,
    get_movie_user_ratings,
    get_watchlist,
    mark_as_watched,
    remove_from_watchlist,
    update_rating,
)
from db.mongodb import (
    add_review,
    delete_review,
    get_movie_reviews,
    get_review,
    update_review,
)
from ui.review_card import render_review_card


def display_movie_hero(movie, movie_id, user_id):
    watchlist = get_watchlist(user_id)

    already_saved = any(
        item["movie_id"] == movie_id
        for item in watchlist
    )

    average = get_average_rating(movie_id)
    rating_count = get_rating_count(movie_id)

    with st.container(key="featured_hero"):
        details_col, rating_col = st.columns(
            [3, 1],
            gap="large",
            vertical_alignment="center"
        )

        with details_col:
            st.markdown(
                '<div class="cv-hero-label">'
                'CINEVAULT MOVIE SPOTLIGHT'
                '</div>',
                unsafe_allow_html=True
            )

            title_col, bookmark_col = st.columns(
                [10, 1],
                vertical_alignment="center"
            )

            with title_col:
                st.title(movie["title"])

            with bookmark_col:
                bookmark_clicked = st.button(
                    "🔖 ✓" if already_saved else "🔖",
                    help=(
                        "Remove from watchlist"
                        if already_saved
                        else "Add to watchlist"
                    ),
                    key=f"movie_bookmark_{movie_id}",
                    type="secondary"
                )

                if bookmark_clicked:
                    if already_saved:
                        remove_from_watchlist(user_id, movie_id)
                    else:
                        add_to_watchlist(user_id, movie_id)

                    st.rerun()

            metadata = [
                movie.get("country") or "Country unavailable",
                ", ".join(movie.get("genres") or []),
                f"Catalogue ID: {movie_id}"
            ]

            st.caption(
                " · ".join(item for item in metadata if item)
            )

            st.write(
                movie.get("description")
                or "No description is available for this movie."
            )

            st.caption(
                f"Director: {movie.get('director') or 'Unknown'}"
            )

            actors = movie.get("actors") or []

            st.caption(
                "Cast: "
                + (", ".join(actors) if actors else "Not available")
            )

        with rating_col:
            st.subheader("Community Rating")

            if average is None:
                st.markdown(
                    '<div class="cv-search-not-rated">'
                    'NOT RATED YET'
                    '</div>',
                    unsafe_allow_html=True
                )

            else:
                average = float(average)

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
                    f'<div class="{score_class}">'
                    f'★ {average:.2f}/5'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.caption(
                f"Based on {rating_count} member ratings"
            )


def save_movie_rating(user_id, movie_id, stars):
    existing_rating = get_rating(user_id, movie_id)

    if existing_rating:
        return update_rating(user_id, movie_id, stars)

    return add_rating(user_id, movie_id, stars)


def save_movie_review(
    user_id,
    movie_id,
    review_text,
    spoiler,
    tags,
    existing_review
):
    if existing_review:
        saved = update_review(
            user_id,
            movie_id,
            review_text,
            spoiler,
            tags
        )
    else:
        saved = add_review(
            user_id,
            movie_id,
            review_text,
            spoiler,
            tags
        )

    if not saved:
        return False, False

    try:
        mark_as_watched(user_id, movie_id)
        watched_updated = True

    except Exception:
        watched_updated = False

    return True, watched_updated


COMMUNITY_REVIEW_FETCH_SIZE = 100


def get_community_reviews_with_ratings(
    movie_id,
    hide_spoilers=True,
    sort_by="newest",
    limit=50,
    offset=0
):
    """Combine MongoDB review documents with batched MariaDB star ratings.

    Newest/oldest sorting and pagination are handled by MongoDB. Highest-rated
    sorting is handled here because it depends on rating data stored in MariaDB.
    """
    if sort_by not in ("newest", "oldest", "highest_rated"):
        raise ValueError(
            "sort_by must be 'newest', 'oldest' or 'highest_rated'"
        )

    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise ValueError("limit must be an integer between 1 and 100")

    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    if sort_by == "highest_rated":
        # Fetch all matching reviews in MongoDB-sized pages so the ranking is
        # global, rather than ranking only the first page of reviews.
        reviews = []
        fetch_offset = 0

        while True:
            batch = get_movie_reviews(
                movie_id,
                sort_by="newest",
                hide_spoilers=hide_spoilers,
                limit=COMMUNITY_REVIEW_FETCH_SIZE,
                offset=fetch_offset
            )

            reviews.extend(batch)

            if len(batch) < COMMUNITY_REVIEW_FETCH_SIZE:
                break

            fetch_offset += len(batch)
    else:
        reviews = get_movie_reviews(
            movie_id,
            sort_by=sort_by,
            hide_spoilers=hide_spoilers,
            limit=limit,
            offset=offset
        )

    if not reviews:
        return []

    user_ids = list(dict.fromkeys(review["user_id"] for review in reviews))
    rating_map = get_movie_user_ratings(movie_id, user_ids)

    # Copy the documents before enriching them; do not mutate MongoDB results.
    enriched_reviews = []
    for review in reviews:
        enriched_review = dict(review)
        enriched_review["rating_stars"] = rating_map.get(review["user_id"])
        enriched_reviews.append(enriched_review)

    if sort_by == "highest_rated":
        # Newer reviews come first when ratings are equal.
        enriched_reviews.sort(
            key=lambda review: review["created_at"],
            reverse=True
        )

        # Rated reviews appear before reviews without a rating.
        enriched_reviews.sort(
            key=lambda review: (
                review["rating_stars"] is None,
                -(review["rating_stars"] or 0)
            )
        )

        return enriched_reviews[offset:offset + limit]

    return enriched_reviews


def display_community_reviews(movie_id):
    st.divider()
    st.subheader("Community Reviews")

    hide_spoilers = st.checkbox(
        "Hide spoiler reviews",
        value=True,
        key=f"hide_spoilers_{movie_id}"
    )

    sort_options = {
        "Newest first": "newest",
        "Oldest first": "oldest",
        "Highest rated": "highest_rated"
    }

    selected_sort = st.selectbox(
        "Sort reviews",
        options=list(sort_options.keys()),
        key=f"review_sort_{movie_id}"
    )

    try:
        community_reviews = get_community_reviews_with_ratings(
            movie_id,
            hide_spoilers=hide_spoilers,
            sort_by=sort_options[selected_sort],
            limit=50
        )

    except Exception as error:
        st.error("Unable to retrieve community reviews.")
        st.exception(error)
        return

    if not community_reviews:
        st.info("No community reviews to display.")
        return

    st.caption(
        f"{len(community_reviews)} reviews displayed"
    )

    for review in community_reviews:
        reviewer = get_user_by_id(review["user_id"])

        reviewer_name = (
            reviewer["username"]
            if reviewer
            else "CineVault member"
        )

        member_rating = review.get("rating_stars")

        with st.container(border=True):
            review_col, info_col = st.columns([4, 1])

            with review_col:
                st.markdown(f"**{reviewer_name}**")
                st.write(review["review_text"])

                if review.get("tags"):
                    st.caption(
                        " · ".join(review["tags"])
                    )

            with info_col:
                if member_rating is not None:
                    st.markdown(
                        f"**{'★' * member_rating}{'☆' * (5 - member_rating)}**"
                    )

                else:
                    st.caption("No star rating")

                if review.get("spoiler"):
                    st.warning("Spoiler")

                created_at = review.get("created_at")

                if created_at:
                    st.caption(
                        created_at.strftime("%d %b %Y")
                        if hasattr(created_at, "strftime")
                        else str(created_at)
                    )


def scroll_movie_details_to_top():
    st.html(
        """
        <script>
            function scrollMovieDetailsToTop() {
                const selectors = [
                    "section.main",
                    '[data-testid="stMain"]',
                    '[data-testid="stAppViewContainer"]',
                    '[data-testid="stMainBlockContainer"]'
                ];

                window.scrollTo({
                    top: 0,
                    left: 0,
                    behavior: "instant"
                });

                document.documentElement.scrollTop = 0;
                document.body.scrollTop = 0;

                selectors.forEach(selector => {
                    const element = document.querySelector(selector);

                    if (element) {
                        element.scrollTo({
                            top: 0,
                            left: 0,
                            behavior: "instant"
                        });
                    }
                });
            }

            requestAnimationFrame(() => {
                requestAnimationFrame(
                    scrollMovieDetailsToTop
                );
            });

            setTimeout(scrollMovieDetailsToTop, 100);
            setTimeout(scrollMovieDetailsToTop, 300);
            setTimeout(scrollMovieDetailsToTop, 700);
        </script>
        """,
        unsafe_allow_javascript=True
    )


def movie_details_page(on_return):
    movie_id = st.session_state.selected_movie_id

    if not movie_id:
        st.info("Choose a movie from Home or Search first.")
        return

    st.button(
        f"← Back to {st.session_state.previous_page}",
        on_click=on_return
    )

    try:
        movie = get_movie_details(movie_id)

        if not movie:
            st.error("This movie could not be found.")
            return

        user_id = st.session_state.current_user["user_id"]

        existing_rating = get_rating(user_id, movie_id)
        existing_review = get_review(user_id, movie_id)

        display_movie_hero(movie, movie_id, user_id)

        st.divider()

        render_review_card(
            review=existing_review,
            movie_id=movie_id,
            rating_stars=(
                existing_rating["stars"]
                if existing_rating
                else None
            ),
            on_submit_review=lambda text, spoiler, tags: (
                save_movie_review(
                    user_id,
                    movie_id,
                    text,
                    spoiler,
                    tags,
                    existing_review
                )
            ),
            on_save_rating=lambda stars: (
                save_movie_rating(user_id, movie_id, stars)
            ),
            on_remove_rating=lambda: (
                delete_rating(user_id, movie_id)
            ),
            on_delete=lambda: (
                delete_review(user_id, movie_id)
            ),
            key_prefix="movie_details"
        )

        display_community_reviews(movie_id)

    except Exception as error:
        st.error(
            "Unable to load movie details. "
            "Please check your database connections."
        )
        st.exception(error)

    # Scroll only after the movie page has finished rendering.
    if st.session_state.pop("scroll_to_top_on_details", False):
        scroll_movie_details_to_top()
