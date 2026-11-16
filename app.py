import os

import streamlit as st

HERE = os.path.dirname(os.path.abspath(__file__))
EXTENSIONS = ["png", "jpg", "jpeg", "webp", "svg"]


def find_asset(name):
    """Return the path of assets/<name>.<ext> if one exists, else None."""
    for ext in EXTENSIONS:
        path = os.path.join(HERE, "assets", f"{name}.{ext}")
        if os.path.exists(path):
            return path
    return None


LOGO = find_asset("logo")
ICON = find_asset("icon")

st.set_page_config(
    page_title="Nexora AI | Free AI assistant for everyone",
    page_icon=ICON or "✨",
    initial_sidebar_state="expanded",
)

if LOGO:
    st.logo(LOGO, size="large")

pages = [
    st.Page("chat.py", title="Chat", icon="💬", default=True),
    st.Page("site_pages/about.py", title="About", icon="ℹ️"),
    st.Page("site_pages/privacy.py", title="Privacy", icon="🔒"),
    st.Page("site_pages/terms.py", title="Terms", icon="📄"),
    st.Page("site_pages/feedback.py", title="Feedback", icon="📝"),
]

st.navigation(pages).run()