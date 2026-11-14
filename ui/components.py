
import streamlit as st


def show_branding():
    st.markdown(
        '<div class="cv-logo">CINE<span>VAULT</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cv-tagline">DISCOVER · RATE · REVIEW</div>',
        unsafe_allow_html=True
    )


def actor_initials(actor_name):
    parts = actor_name.replace("-", " ").split()
    return "".join(part[0].upper() for part in parts[:2])
