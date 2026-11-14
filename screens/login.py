
import streamlit as st

from db.authentication import (
    authenticate_user,
    create_user,
    get_demo_users,
)

from ui.components import show_branding


DEMO_PROFILES = {
    "Active Member": {
        "username": "sample_user_06",
        "description": (
            "An active community member with ratings and written reviews."
        )
    },
    "Reviewer": {
        "username": "sample_user_11",
        "description": (
            "A review-focused member with an extensive review history."
        )
    },
    "Movie Explorer": {
        "username": "sample_user_07",
        "description": (
            "Explore watched movies, saved titles and community reviews."
        )
    }
}


def sign_in_member(username, password):
    try:
        user = authenticate_user(username, password)

        if user is None:
            st.error("Incorrect username or password.")
            return

        st.session_state.current_user = user
        st.session_state.page = "Home"
        st.session_state.navigation_choice = "Home"
        st.rerun()

    except Exception:
        st.error(
            "Unable to sign in. Please check your database connection."
        )


def register_member(username, password, confirm_password):
    if password != confirm_password:
        st.error("Your passwords do not match.")
        return

    try:
        user = create_user(username, password)

        st.session_state.current_user = user
        st.session_state.page = "Home"
        st.session_state.navigation_choice = "Home"

        st.success("Your CineVault account has been created.")
        st.rerun()

    except ValueError as error:
        st.error(str(error))

    except Exception:
        st.error(
            "Unable to create your account. Please try again."
        )


def login_page():
    left_col, right_col = st.columns(
        [1, 1],
        gap="large",
        vertical_alignment="center"
    )

    with left_col:
        show_branding()

        st.write("")

        st.markdown(
            '<div class="cv-eyebrow">YOUR MOVIE COMMUNITY</div>',
            unsafe_allow_html=True
        )

        st.title("Your next favourite movie starts here.")

        st.write(
            "Discover movies, explore community opinions, "
            "and keep track of what you love watching."
        )

        st.write("")
        st.write("")

        st.caption(
            "A space to discover, rate and review movies."
        )

    with right_col:
        with st.container(border=True):
            st.subheader("Welcome to CineVault")

            st.caption(
                "Sign in to discover, rate and review movies."
            )

            login_tab, register_tab = st.tabs(
                ["Sign In", "Create Account"]
            )

            with login_tab:
                with st.form("member_login_form"):
                    username = st.text_input(
                        "Username",
                        placeholder="Enter your username"
                    )

                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password"
                    )

                    submitted = st.form_submit_button(
                        "Sign In",
                        type="primary",
                        use_container_width=True
                    )

                if submitted:
                    if not username.strip() or not password:
                        st.warning(
                            "Please enter both your username and password."
                        )
                    else:
                        sign_in_member(username, password)

            with register_tab:
                st.caption(
                    "Create your own CineVault member account."
                )

                with st.form("member_registration_form"):
                    new_username = st.text_input(
                        "Choose a username",
                        placeholder="At least 3 characters"
                    )

                    new_password = st.text_input(
                        "Create a password",
                        type="password",
                        placeholder="At least 8 characters"
                    )

                    confirm_password = st.text_input(
                        "Confirm password",
                        type="password",
                        placeholder="Re-enter your password"
                    )

                    register_submitted = st.form_submit_button(
                        "Create Account",
                        type="primary",
                        use_container_width=True
                    )

                if register_submitted:
                    register_member(
                        new_username,
                        new_password,
                        confirm_password
                    )

        st.write("")

        with st.container(border=True):
            st.subheader("Explore with a Demo Profile")

            st.caption(
                "Try CineVault using one of our prepared member profiles."
            )

            try:
                demo_users = get_demo_users()

                demo_lookup = {
                    user["username"]: user
                    for user in demo_users
                }

                available_profiles = {
                    name: demo_lookup[details["username"]]
                    for name, details in DEMO_PROFILES.items()
                    if details["username"] in demo_lookup
                }

                if not available_profiles:
                    st.warning(
                        "No demo profiles are currently available."
                    )

                else:
                    selected_profile = st.selectbox(
                        "Choose your profile",
                        options=list(available_profiles.keys()),
                        key="demo_profile_choice"
                    )

                    st.caption(
                        DEMO_PROFILES[selected_profile]["description"]
                    )

                    if st.button(
                        "Continue as " + selected_profile,
                        type="primary",
                        use_container_width=True
                    ):
                        selected_user = available_profiles[
                            selected_profile
                        ]

                        st.session_state.current_user = {
                            "user_id": selected_user["user_id"],
                            "username": selected_user["username"],
                            "account_type": "demo"
                        }

                        st.session_state.page = "Home"
                        st.session_state.navigation_choice = "Home"
                        st.rerun()

            except Exception:
                st.error(
                    "Unable to retrieve demo profiles. "
                    "Please check MariaDB."
                )
