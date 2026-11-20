
import html
import streamlit as st


def format_review_date(value):
    if not value:
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%d %b %Y")

    return str(value)


def render_review_card(
    review,
    movie_id=None,
    rating_stars=None,
    movie_title=None,
    on_submit_review=None,
    on_save_rating=None,
    on_remove_rating=None,
    on_delete=None,
    on_view_movie=None,
    key_prefix="review"
):
    movie_id = movie_id or (
        review["movie_id"] if review else None
    )

    if movie_id is None:
        raise ValueError("A movie ID is required.")

    card_key = f"{key_prefix}_{movie_id}"
    editing_key = f"{card_key}_editing"
    rating_key = f"{card_key}_rating"
    delete_key = f"{card_key}_delete_pending"
    notice_key = f"{card_key}_notice"

    if editing_key not in st.session_state:
        st.session_state[editing_key] = False

    has_review = review is not None
    has_rating = rating_stars is not None
    complete = has_review and has_rating
    editing = st.session_state[editing_key]

    if complete:
        card_state = "complete"
        status_text = "✓ CONTRIBUTION COMPLETE"
        status_color = "#75D9A4"

    elif has_review:
        card_state = "pending"
        status_text = "RATING PENDING"
        status_color = "#E6B85C"

    elif has_rating:
        card_state = "pending"
        status_text = "REVIEW PENDING"
        status_color = "#E6B85C"

    else:
        card_state = "pending"
        status_text = "RATING & REVIEW PENDING"
        status_color = "#E6B85C"

    st.markdown(
        """
        <style>
        div[class*="st-key-cv_review_card_complete"] {
            background: linear-gradient(
                135deg,
                rgba(31, 72, 53, 0.34),
                rgba(20, 37, 30, 0.52)
            );
            border: 1px solid rgba(91, 178, 126, 0.75);
            border-radius: 12px;
            padding: 0.5rem 1rem;
            box-shadow: 0 0 20px rgba(91, 178, 126, 0.16);
        }

        div[class*="st-key-cv_review_card_pending"] {
            background: linear-gradient(
                135deg,
                rgba(86, 65, 28, 0.18),
                rgba(38, 32, 22, 0.38)
            );
            border: 1px solid rgba(199, 153, 69, 0.65);
            border-radius: 12px;
            padding: 0.5rem 1rem;
            box-shadow: 0 0 16px rgba(199, 153, 69, 0.10);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    container_key = (
        f"cv_review_card_{card_state}_{key_prefix}_{movie_id}"
    )

    with st.container(border=True, key=container_key):
        heading_col, status_col = st.columns(
            [3, 2],
            vertical_alignment="center"
        )

        with heading_col:
            st.markdown(
                f"**{html.escape(movie_title)}**"
                if movie_title
                else "**Your Review**"
            )

        with status_col:
            st.markdown(
                f'<div style="text-align:right;'
                f'color:{status_color};'
                f'font-size:11px;'
                f'font-weight:800;'
                f'letter-spacing:0.7px;">'
                f'{status_text}'
                f'</div>',
                unsafe_allow_html=True
            )

        if has_review and not editing:
            date_text = format_review_date(
                review.get("created_at")
            )

            if date_text:
                st.caption(date_text)

            if review.get("spoiler"):
                st.warning("This review contains spoilers.")

            review_text = html.escape(
                review.get("review_text") or ""
            )

            st.markdown(
                review_text.replace("\n", "  \n")
            )

            tags = review.get("tags") or []

            if tags:
                tag_html = "".join(
                    (
                        '<span style="display:inline-block;'
                        'background:rgba(150,150,160,0.12);'
                        'border:1px solid rgba(150,150,160,0.25);'
                        'border-radius:6px;'
                        'padding:4px 9px;'
                        'margin-right:6px;'
                        'margin-top:6px;'
                        'font-size:12px;">'
                        f'{html.escape(str(tag))}'
                        '</span>'
                    )
                    for tag in tags
                )

                st.markdown(
                    tag_html,
                    unsafe_allow_html=True
                )

        else:
            st.caption(
                "Update your review."
                if editing
                else "Share your thoughts with the CineVault community."
            )

            with st.form(f"{card_key}_review_form"):
                review_text = st.text_area(
                    "Write your review",
                    value=(
                        review.get("review_text", "")
                        if review
                        else ""
                    ),
                    max_chars=2000
                )

                spoiler = st.checkbox(
                    "This review contains spoilers",
                    value=(
                        review.get("spoiler", False)
                        if review
                        else False
                    )
                )

                tags = st.multiselect(
                    "Review tags",
                    [
                        "acting",
                        "story",
                        "ending",
                        "pacing",
                        "visuals",
                        "music",
                        "funny",
                        "scary",
                        "emotional",
                        "action",
                        "family",
                        "characters",
                        "realistic",
                        "rewatchable",
                        "overrated"
                    ],
                    default=(
                        review.get("tags", [])
                        if review
                        else []
                    )
                )

                submitted = st.form_submit_button(
                    "Save Changes" if editing else "Submit Review",
                    type="primary"
                )

            if submitted:
                if not review_text.strip():
                    st.warning("Please write something before submitting.")

                elif on_submit_review is None:
                    st.error("Review submission is unavailable.")

                else:
                    try:
                        result = on_submit_review(
                            review_text,
                            spoiler,
                            tags
                        )

                        saved = (
                            result[0]
                            if isinstance(result, tuple)
                            else result
                        )

                        watched_updated = (
                            result[1]
                            if isinstance(result, tuple)
                            and len(result) > 1
                            else True
                        )

                        if saved is False:
                            st.warning("Your review was not changed.")

                        else:
                            st.session_state[editing_key] = False

                            st.session_state[notice_key] = (
                                "Your review has been saved."
                                if watched_updated
                                else (
                                    "Your review was saved, but "
                                    "watched history could not be updated."
                                )
                            )

                            st.rerun()

                    except ValueError as error:
                        st.error(str(error))

                    except Exception as error:
                        st.error("Unable to save your review.")
                        st.exception(error)

        st.divider()
        st.markdown("**YOUR RATING**")

        if has_rating:
            st.caption(f"Your current rating: {rating_stars}/5")
        else:
            st.caption("Select a star to rate this movie.")

        selected_rating = st.feedback(
            "stars",
            key=rating_key,
            default=(
                rating_stars - 1
                if has_rating
                else None
            )
        )

        rating_col, remove_col = st.columns([1, 1])

        with rating_col:
            rating_changed = (
                selected_rating is not None
                and selected_rating + 1 != rating_stars
            )

            if st.button(
                "Save Rating",
                key=f"{card_key}_save_rating",
                type="primary",
                disabled=(
                    selected_rating is None
                    or not rating_changed
                    or on_save_rating is None
                )
            ):
                try:
                    saved = on_save_rating(selected_rating + 1)

                    if saved is not False:
                        st.session_state[notice_key] = (
                            "Your rating has been saved."
                        )
                        st.rerun()

                    else:
                        st.warning("Your rating was not changed.")

                except ValueError as error:
                    st.error(str(error))

                except Exception as error:
                    st.error("Unable to save your rating.")
                    st.exception(error)

        with remove_col:
            if has_rating and on_remove_rating is not None:
                if st.button(
                    "Remove Rating",
                    key=f"{card_key}_remove_rating"
                ):
                    try:
                        on_remove_rating()
                        st.session_state.pop(rating_key, None)
                        st.rerun()

                    except Exception as error:
                        st.error("Unable to remove your rating.")
                        st.exception(error)

        if notice_key in st.session_state:
            st.success(st.session_state.pop(notice_key))

        st.divider()

        action_col, spacer_col = st.columns([3, 2])

        with action_col:
            if on_view_movie is not None:
                if st.button(
                    "View Movie",
                    key=f"{card_key}_view_movie"
                ):
                    on_view_movie(movie_id)

        with spacer_col:
            edit_col, delete_col = st.columns(2)

            with edit_col:
                if has_review and not editing:
                    if st.button(
                        "Edit",
                        key=f"{card_key}_edit",
                        use_container_width=True
                    ):
                        st.session_state[editing_key] = True
                        st.rerun()

                elif editing:
                    if st.button(
                        "Cancel",
                        key=f"{card_key}_cancel_edit",
                        use_container_width=True
                    ):
                        st.session_state[editing_key] = False
                        st.rerun()

            with delete_col:
                if has_review and not editing and on_delete is not None:
                    if st.button(
                        "Delete",
                        key=f"{card_key}_delete",
                        use_container_width=True
                    ):
                        st.session_state[delete_key] = True
                        st.rerun()

        if st.session_state.get(delete_key, False):
            st.warning(
                "Are you sure you want to delete this review? "
                "This action cannot be undone."
            )

            cancel_col, confirm_col = st.columns(2)

            with cancel_col:
                if st.button(
                    "Cancel",
                    key=f"{card_key}_cancel_delete",
                    use_container_width=True
                ):
                    st.session_state[delete_key] = False
                    st.rerun()

            with confirm_col:
                if st.button(
                    "Confirm Delete",
                    key=f"{card_key}_confirm_delete",
                    type="primary",
                    use_container_width=True
                ):
                    try:
                        deleted = on_delete()

                        if deleted is False:
                            st.warning(
                                "The review could not be deleted."
                            )
                        else:
                            st.session_state[delete_key] = False
                            st.rerun()

                    except Exception as error:
                        st.error("Unable to delete the review.")
                        st.exception(error)
