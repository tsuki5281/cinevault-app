
import streamlit as st

st.set_page_config(
    page_title="CineVault",
    page_icon="C",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from ui.styles import apply_styles
from screens.login import login_page
from screens.home import home_page
from screens.search import search_page, SEARCH_PAGE_SIZE
from screens.movie_details import movie_details_page
from screens.activity import my_activity_page


def initialize_session_state():
    defaults = {
        "current_user": None,
        "page": "Home",
        "navigation_choice": "Home",
        "selected_movie_id": None,
        "previous_page": "Home",
        "home_genre_selection": [],
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
        "curated_visible_count": SEARCH_PAGE_SIZE
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def update_navigation():
    st.session_state.page = st.session_state.navigation_choice


def open_movie_details(movie_id, source_page):
    st.session_state.selected_movie_id = movie_id
    st.session_state.previous_page = source_page
    st.session_state.page = "Movie Details"
    st.session_state.scroll_to_top_on_details = True


def return_to_previous_page():
    destination = st.session_state.get("previous_page", "Home")

    st.session_state.page = destination
    st.session_state.navigation_choice = destination


def sign_out():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()


def display_sidebar():
    current_user = st.session_state.current_user

    st.sidebar.markdown(
        '<div class="cv-logo">CINE<span>VAULT</span></div>',
        unsafe_allow_html=True
    )

    st.sidebar.caption(
        f"Signed in as {current_user['username']}"
    )

    st.sidebar.caption(
        "DEMO PROFILE"
        if current_user["account_type"] == "demo"
        else "MEMBER ACCOUNT"
    )

    st.sidebar.divider()

    st.sidebar.radio(
        "Navigation",
        ["Home", "Search", "My Activity"],
        key="navigation_choice",
        on_change=update_navigation
    )

    st.sidebar.divider()

    st.sidebar.button(
        "Sign Out",
        use_container_width=True,
        on_click=sign_out
    )


def main():
    initialize_session_state()
    apply_styles()

    if st.session_state.current_user is None:
        login_page()
        st.stop()

    display_sidebar()

    current_page = st.session_state.page

    if current_page == "Home":
        home_page(open_movie_details)

    elif current_page == "Search":
        search_page(open_movie_details)

    elif current_page == "My Activity":
        my_activity_page()

    elif current_page == "Movie Details":
        movie_details_page(return_to_previous_page)


if __name__ == "__main__":
    main()
