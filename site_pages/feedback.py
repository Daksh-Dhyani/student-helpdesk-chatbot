import streamlit as st

from src.db import DBError, add_feedback, db_ready

MAX_MESSAGE = 1000
MAX_CONTACT = 200
SESSION_LIMIT = 3  # feedback messages per visit

KINDS = ["Bug report", "Suggestion", "Wrong university answer", "Other"]

st.title("📝 Feedback")
st.write("Found a bug, a wrong answer, or have an idea? Tell me. Please "
         "don't include passwords or other private details.")

try:
    signed_in = st.user.is_logged_in
    user_email = st.user.email if signed_in else ""
except Exception:
    signed_in, user_email = False, ""

if signed_in:
    st.caption("You're signed in, so your email is saved with this feedback.")

st.session_state.setdefault("feedback_count", 0)

if not db_ready():
    st.info("Feedback isn't available right now. Please try again later.")
elif st.session_state.feedback_count >= SESSION_LIMIT:
    st.info("Thanks! You've sent the maximum number of feedback messages "
            "for this visit.")
else:
    with st.form("feedback_form", clear_on_submit=True):
        kind = st.selectbox("What is this about?", KINDS)
        message = st.text_area("Your message", max_chars=MAX_MESSAGE,
                               height=160)
        contact = st.text_input("Contact (optional)", max_chars=MAX_CONTACT,
                                help="Only if you want a reply.")
        sent = st.form_submit_button("Send feedback")

    if sent:
        message = " ".join(message.split()) if message else ""
        if len(message) < 5:
            st.warning("Please write a little more so I can understand.")
        else:
            try:
                add_feedback(kind, message, contact.strip(), user_email)
                st.session_state.feedback_count += 1
                st.success("Thank you! Your feedback was sent.")
            except DBError:
                st.error("Couldn't send your feedback right now. Please try "
                         "again later.")