import streamlit as st

st.title("🔒 Privacy")
st.caption("Last updated: 16 November 2026. This is a plain-language "
           "summary, not legal advice.")

st.markdown("""
This is a student project. Here is what happens to your data.

### If you use it without signing in
- Your chat is kept only in your browser session. It is **not saved in our
  database** and is gone when you refresh or close the page.
- Your messages are sent to **Google's Gemini API** so the AI can reply.

### If you sign in with Google
- Google tells this site your **email address and name**. The name is only
  shown on screen. Your email is used to identify your account.
- Your chats (titles and messages) are **stored in a Supabase database**
  linked to your email, so you can open them on other devices.
- A counter of how many AI answers you used each day is stored with your
  email, to enforce the daily limit.
- Your messages are sent to Google's Gemini API to get replies.

### Uploaded syllabus files
- A file you upload is read during your session and sent to Google's Gemini
  API together with your questions.
- The file itself is not saved in our database. If an answer quotes part of
  it and you are signed in, that answer is saved as part of your chat.

### Feedback
- If you send feedback, we store your message, the category, the optional
  contact detail you type, and your email if you are signed in.

### Google's handling of your messages
- Google processes your messages to generate replies. Depending on the terms
  of the Gemini API service used, Google may keep and use submitted content.
  See Google's Gemini API terms for details.

### Cookies and logs
- Signing in uses a cookie so you stay signed in.
- The hosting service (Streamlit Community Cloud) and the database service
  (Supabase) may record technical information such as IP addresses in their
  own logs. This site does not add advertising or tracking tools.

### Please don't share
Passwords, ID or card numbers, or other confidential or sensitive personal
information. Treat this like any public AI chat.

### Deleting your data
- Use the **🗑** button next to a chat in the sidebar to delete one chat.
- Open **🔒 Your saved chats** in the sidebar to delete all your saved chats.
- To remove your usage counters or feedback, send a message on the Feedback
  page saying "delete my data" while signed in.
""")