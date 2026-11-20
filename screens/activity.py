
import streamlit as st

from db.catalogue import get_movie_details
from db.mariadb import (
    add_rating,
    delete_rating,
    get_user_ratings,
    get_watched_movies,
    get_watchlist,
    mark_as_watched,
    remove_from_watchlist,
    remove_watched_status,
    update_rating,
)
from db.mongodb import (
    add_review,
    delete_review,
    get_user_reviews,
    update_review,
)
from ui.review_card import render_review_card


def format_activity_date(value):
    if not value:
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%d %b %Y")

    return str(value)


def activity_sort_date(review, rating):
    dates = []

    if review and review.get("created_at"):
        dates.append(review["created_at"])

    if rating and rating.get("updated_at"):
        dates.append(rating["updated_at"])

    if not dates:
        return ""

    latest = max(
        dates,
        key=lambda value: (
            value.isoformat()
            if hasattr(value, "isoformat")
            else str(value)
        )
    )

    return (
        latest.isoformat()
        if hasattr(latest, "isoformat")
        else str(latest)
    )


def open_movie_from_activity(movie_id):
    st.session_state.selected_movie_id = movie_id
    st.session_state.previous_page = "My Activity"
    st.session_state.page = "Movie Details"
    st.session_state.scroll_to_top_on_details = True
    st.rerun()


def save_activity_rating(user_id, movie_id, stars):
    ratings = {
        item["movie_id"]: item
        for item in get_user_ratings(user_id)
    }

    if movie_id in ratings:
        saved = update_rating(user_id, movie_id, stars)
    else:
        saved = add_rating(user_id, movie_id, stars)

    # Keep rating actions consistent with Movie Details.
    try:
        mark_as_watched(user_id, movie_id)
    except Exception:
        pass

    return saved


def save_activity_review(
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


def build_contribution_list(ratings, reviews):
    rating_lookup = {
        item["movie_id"]: item
        for item in ratings
    }

    review_lookup = {
        item["movie_id"]: item
        for item in reviews
    }

    all_movie_ids = (
        set(rating_lookup.keys())
        | set(review_lookup.keys())
    )

    contributions = []

    for movie_id in all_movie_ids:
        rating = rating_lookup.get(movie_id)
        review = review_lookup.get(movie_id)

        contributions.append({
            "movie_id": movie_id,
            "rating": rating,
            "review": review,
            "title": (
                rating.get("title")
                if rating
                else None
            ),
            "latest_activity": activity_sort_date(
                review,
                rating
            )
        })

    contributions.sort(
        key=lambda item: item["latest_activity"],
        reverse=True
    )

    return contributions


def display_contribution_card(item, user_id):
    movie_id = item["movie_id"]
    rating = item["rating"]
    review = item["review"]

    title = item["title"]

    if not title:
        movie = get_movie_details(movie_id)
        title = movie["title"] if movie else movie_id

    render_review_card(
        review=review,
        movie_id=movie_id,
        movie_title=title,
        rating_stars=(
            rating["stars"]
            if rating
            else None
        ),
        on_submit_review=lambda text, spoiler, tags: (
            save_activity_review(
                user_id,
                movie_id,
                text,
                spoiler,
                tags,
                review
            )
        ),
        on_save_rating=lambda stars: (
            save_activity_rating(
                user_id,
                movie_id,
                stars
            )
        ),
        on_remove_rating=lambda: (
            delete_rating(user_id, movie_id)
        ),
        on_delete=lambda: (
            delete_review(user_id, movie_id)
        ),
        on_view_movie=open_movie_from_activity,
        key_prefix="activity_contribution"
    )


def display_contributions(contributions, user_id):
    st.markdown(
        '<div class="cv-eyebrow">YOUR MOVIE JOURNEY</div>',
        unsafe_allow_html=True
    )

    st.subheader("My Contributions")

    st.caption(
        "Keep track of the movies you've rated and reviewed."
    )

    if not contributions:
        st.info(
            "You haven't rated or reviewed any movies yet. "
            "Explore the collection to get started."
        )
        return

    for item in contributions:
        try:
            display_contribution_card(item, user_id)

        except Exception as error:
            st.error(
                f"Unable to display {item['movie_id']}."
            )
            st.exception(error)


def display_watched_history(watched_movies):
    st.markdown(
        '<div class="cv-eyebrow">YOUR WATCH HISTORY</div>',
        unsafe_allow_html=True
    )

    st.subheader("Watched History")

    st.caption(
        "Movies you've rated or reviewed are automatically added to your watched history."
    )

    if not watched_movies:
        st.info(
            "Your watched history is empty. "
            "Rate or review a movie to add it here."
        )
        return

    for movie in watched_movies:
        movie_id = movie["movie_id"]

        with st.container(border=True):
            title_col, date_col = st.columns(
                [3, 1],
                vertical_alignment="center"
            )

            with title_col:
                st.markdown(f"**{movie['title']}**")
                st.caption(movie_id)

            with date_col:
                st.caption(
                    format_activity_date(
                        movie.get("watched_at")
                    )
                )

            view_col, remove_col = st.columns(2)

            with view_col:
                st.button(
                    "View Movie",
                    key=f"watched_view_{movie_id}",
                    use_container_width=True,
                    on_click=open_movie_from_activity,
                    args=(movie_id,)
                )

            with remove_col:
                if st.button(
                    "Remove from History",
                    key=f"watched_remove_{movie_id}",
                    use_container_width=True
                ):
                    remove_watched_status(
                        st.session_state.current_user["user_id"],
                        movie_id
                    )
                    st.rerun()


def display_watchlist(watchlist, user_id):
    st.markdown(
        '<div class="cv-eyebrow">SAVED FOR LATER</div>',
        unsafe_allow_html=True
    )

    st.subheader("My Watchlist")

    st.caption(
        "Movies you've bookmarked for another time."
    )

    if not watchlist:
        st.info(
            "Your watchlist is empty. "
            "Bookmark movies from their details page to save them here."
        )
        return

    for movie in watchlist:
        movie_id = movie["movie_id"]

        with st.container(border=True):
            title_col, date_col = st.columns(
                [3, 1],
                vertical_alignment="center"
            )

            with title_col:
                st.markdown(
                    f"🔖 **{movie['title']}**"
                )

                st.caption(movie_id)

            with date_col:
                st.caption(
                    format_activity_date(
                        movie.get("added_at")
                    )
                )

            view_col, remove_col = st.columns(2)

            with view_col:
                st.button(
                    "View Movie",
                    key=f"watchlist_view_{movie_id}",
                    use_container_width=True,
                    on_click=open_movie_from_activity,
                    args=(movie_id,)
                )

            with remove_col:
                if st.button(
                    "Remove Bookmark",
                    key=f"watchlist_remove_{movie_id}",
                    use_container_width=True
                ):
                    remove_from_watchlist(user_id, movie_id)
                    st.rerun()


def my_activity_page():
    user = st.session_state.current_user
    user_id = user["user_id"]

    st.markdown(
        '<div class="cv-eyebrow">YOUR CINEVAULT PROFILE</div>',
        unsafe_allow_html=True
    )

    st.title("My Activity")

    st.caption(
        f"Your movie journey, contributions and saved titles · "
        f"{user['username']}"
    )

    try:
        ratings = get_user_ratings(user_id)
        reviews = get_user_reviews(user_id, limit=100)
        watched_movies = get_watched_movies(user_id)
        watchlist = get_watchlist(user_id)

    except Exception as error:
        st.error(
            "Unable to load your activity. "
            "Please check your database connections."
        )
        st.exception(error)
        return

    contributions = build_contribution_list(
        ratings,
        reviews
    )

    st.divider()

    rating_col, review_col, watched_col, watchlist_col = st.columns(4)

    with rating_col:
        st.metric(
            "Ratings",
            len(ratings)
        )

    with review_col:
        st.metric(
            "Reviews",
            len(reviews)
        )

    with watched_col:
        st.metric(
            "Watched",
            len(watched_movies)
        )

    with watchlist_col:
        st.metric(
            "Watchlist",
            len(watchlist)
        )

    st.divider()

    contributions_tab, watched_tab, watchlist_tab = st.tabs(
        [
            f"My Contributions ({len(contributions)})",
            f"Watched History ({len(watched_movies)})",
            f"My Watchlist ({len(watchlist)})"
        ]
    )

    with contributions_tab:
        display_contributions(
            contributions,
            user_id
        )

    with watched_tab:
        display_watched_history(watched_movies)

    with watchlist_tab:
        display_watchlist(
            watchlist,
            user_id
        )
