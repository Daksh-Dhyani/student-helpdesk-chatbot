import streamlit as st

st.set_page_config(
    page_title="Nexora AI | AI assistant for university students",
    page_icon="✨",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page("chat.py", title="Chat", icon="💬", default=True),
    st.Page("site_pages/about.py", title="About", icon="ℹ️"),
    st.Page("site_pages/privacy.py", title="Privacy", icon="🔒"),
    st.Page("site_pages/terms.py", title="Terms", icon="📄"),
    st.Page("site_pages/feedback.py", title="Feedback", icon="📝"),
]

st.navigation(pages).run()