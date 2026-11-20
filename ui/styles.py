
import streamlit as st


APP_CSS = """
<style>
    .cv-logo {
        color: var(--text-color);
        font-size: 34px;
        font-weight: 850;
        letter-spacing: 4px;
        margin-bottom: 4px;
    }

    .cv-logo span {
        color: #E50914;
    }

    .cv-tagline {
        color: var(--text-color);
        font-size: 10px;
        letter-spacing: 3px;
        opacity: 0.65;
    }

    .cv-eyebrow {
        color: #E50914;
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .cv-hero-label {
        color: #E50914;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .st-key-featured_hero {
        background: linear-gradient(
            115deg,
            #25252C 0%,
            #1B1B21 65%,
            #35191F 100%
        );
        border: 1px solid rgba(229, 9, 20, 0.3);
        border-left: 4px solid #E50914;
        border-radius: 16px;
        padding: 1.5rem 1.5rem 1rem;
    }

    .st-key-featured_hero h1 {
        font-size: clamp(2rem, 4vw, 3.2rem);
        letter-spacing: -1px;
    }

    .st-key-featured_hero [data-testid="stMetricValue"] {
        color: #E6B85C;
        font-size: 2.5rem;
    }

    .st-key-featured_hero [data-testid="stMetricLabel"] {
        letter-spacing: 1px;
    }

    [class*="st-key-home_movie_highest_"] {
        background: linear-gradient(
            145deg,
            rgba(48, 28, 32, 0.55),
            rgba(25, 25, 30, 0.8)
        );
        border-top: 2px solid #E50914;
        border-radius: 12px;
        padding: 0.65rem;
        min-height: 230px;
    }

    [class*="st-key-home_movie_reviewed_"] {
        background: linear-gradient(
            145deg,
            rgba(43, 39, 30, 0.55),
            rgba(25, 25, 30, 0.8)
        );
        border-top: 2px solid #C99D4D;
        border-radius: 12px;
        padding: 0.65rem;
        min-height: 230px;
    }

    .cv-card-rank {
        color: rgba(255, 255, 255, 0.22);
        font-size: 30px;
        font-weight: 850;
        letter-spacing: -1px;
    }

    .cv-card-kicker {
        color: #B7A98D;
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .cv-rating-tier {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: 1px;
        margin-top: 8px;
        margin-bottom: 4px;
    }

    .cv-rating-tier-high {
        color: #75D9A4;
        background: rgba(46, 160, 100, 0.15);
        border: 1px solid rgba(117, 217, 164, 0.45);
    }

    .cv-rating-tier-mid {
        color: #E6B85C;
        background: rgba(230, 184, 92, 0.13);
        border: 1px solid rgba(230, 184, 92, 0.4);
    }

    .cv-rating-tier-low {
        color: #FF7882;
        background: rgba(229, 9, 20, 0.15);
        border: 1px solid rgba(255, 120, 130, 0.5);
    }

    .cv-card-rating-high {
        color: #75D9A4;
        font-size: 23px;
        font-weight: 850;
        margin-top: 8px;
    }

    .cv-card-rating-mid {
        color: #E6B85C;
        font-size: 23px;
        font-weight: 850;
        margin-top: 8px;
    }

    .cv-card-rating-low {
        color: #FF7882;
        font-size: 23px;
        font-weight: 850;
        margin-top: 8px;
    }

    .cv-card-review-count {
        color: #E6B85C;
        font-size: 22px;
        font-weight: 800;
        margin-top: 12px;
    }

    .cv-spoiler-alert {
        display: block;
        width: fit-content;
        color: #FFB3BA;
        background: rgba(229, 9, 20, 0.22);
        border: 1px solid rgba(229, 9, 20, 0.75);
        border-radius: 6px;
        padding: 6px 8px;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: 0.5px;
        margin: 8px 0 14px;
    }

    .cv-spoiler-safe {
        display: block;
        width: fit-content;
        color: #A5A5AE;
        background: rgba(150, 150, 160, 0.09);
        border: 1px solid rgba(150, 150, 160, 0.25);
        border-radius: 6px;
        padding: 6px 8px;
        font-size: 10px;
        font-weight: 750;
        margin: 8px 0 14px;
    }

    .cv-genre-caption {
        color: var(--text-color);
        opacity: 0.65;
        font-size: 0.85rem;
    }

    .cv-actor-initials {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 58px;
        height: 58px;
        border-radius: 50%;
        background: linear-gradient(135deg, #48232C, #19191F);
        border: 1px solid rgba(229, 9, 20, 0.65);
        color: #F2C6C9;
        font-size: 19px;
        font-weight: 850;
        margin-bottom: 12px;
    }

    [class*="st-key-actor_spotlight_"] {
        background: linear-gradient(
            145deg,
            rgba(45, 30, 36, 0.7),
            rgba(25, 25, 31, 0.95)
        );
        border-top: 2px solid #E50914;
        border-radius: 14px;
        padding: 1rem;
        min-height: 345px;
    }

    [class*="st-key-actor_featured_movie_"] {
        background: linear-gradient(
            110deg,
            rgba(201, 157, 77, 0.17),
            rgba(229, 9, 20, 0.09)
        );
        border-left: 3px solid #C99D4D;
        border-radius: 8px;
        padding: 0.65rem 0.85rem;
        margin: 0.5rem 0 1rem;
    }

    .cv-actor-label {
        color: #E56B72;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .cv-featured-movie-label {
        color: #E6B85C;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .cv-actor-film-count {
        color: #C8A66C;
        font-size: 12px;
        font-weight: 700;
    }

    .cv-card-rating-high,
    .cv-card-rating-mid,
    .cv-card-rating-low {
        font-size: 21px;
    }

    .cv-search-rating {
        color: #E6B85C;
        font-weight: 750;
    }

    [class*="st-key-search_movie_card_"] {
        background: linear-gradient(
            145deg,
            rgba(38, 36, 43, 0.95),
            rgba(24, 24, 29, 0.98)
        );
        border: 1px solid #393940;
        border-top: 2px solid #C99D4D;
        border-radius: 12px;
        padding: 0.9rem;
        height: 355px;
        box-sizing: border-box;
    }

    [class*="st-key-search_movie_card_"] [data-testid="stVerticalBlock"] {
        display: flex;
        flex-direction: column;
        min-height: 315px;
    }

    [class*="st-key-search_movie_card_"] [data-testid="stButton"] {
        margin-top: auto;
    }

    .cv-search-title {
        min-height: 3.2em;
        max-height: 3.2em;
        overflow: hidden;
        line-height: 1.5;
        font-weight: 750;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }

    .cv-search-genres {
        min-height: 4.2em;
        max-height: 4.2em;
        overflow: hidden;
        line-height: 1.4;
        opacity: 0.7;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
    }

    .cv-search-rating-slot {
        min-height: 4.4rem;
        margin-top: 0.4rem;
    }

    .cv-search-rating-count {
        color: #AAAAAF;
        font-size: 12px;
        margin-top: 4px;
    }

    .cv-search-not-rated {
        color: #AAAAAF;
        font-size: 15px;
        font-weight: 750;
        padding-top: 8px;
    }
</style>
"""


def apply_styles():
    st.markdown(
        APP_CSS,
        unsafe_allow_html=True
    )
