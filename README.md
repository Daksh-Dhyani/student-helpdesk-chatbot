# Student Helpdesk Chatbot

A free AI assistant for university students. It answers general questions on almost any subject, gives **verified answers** about Chandigarh University (exams, attendance, fees, hostel, library, transport, scholarships), helps students study from an uploaded syllabus, and gives general career guidance for data roles.

**Live app:** https://nexora-ai-global.streamlit.app

![Student Helpdesk screenshot](screenshots/chat_demo.png)

## Features

- **General AI assistant** (Google Gemini): explanations, coding help, writing, study help.
- **Verified university answers** from `data/faq.csv`, matched with TF-IDF and cosine similarity (scikit-learn). Answers do not come from the AI's memory.
- **Career guidance** from `data/career_guide.md`, labelled as general industry advice.
- **Study helper:** upload a syllabus (PDF or text) for study plans, notes and practice questions.
- **Optional Google sign-in** (Streamlit login). Signed-in users get chats saved across devices (Supabase).
- **Multiple chats, Copy and Regenerate.**
- **Usage limits:** per visit, per user per day, and site-wide per day, to stay within free quotas.
- **Prompt-injection hardening:** user text, chat history and uploads are treated as untrusted data. This reduces the risk, but does not remove it.
- **Pages:** About, Privacy, Terms and a Feedback form (stored in Supabase).

## Tech stack

Python, Streamlit, scikit-learn, Google Gemini API (`google-genai`), Supabase (REST), Google OAuth (Streamlit `st.login`).

## Project structure

```
app.py              page navigation
chat.py             chat page
site_pages/         About, Privacy, Terms, Feedback
src/chatbot.py      verified-answer matching
src/db.py           Supabase access (chats, usage, feedback)
data/faq.csv        verified university facts
data/career_guide.md  general career guidance
requirements.txt
```

## Run locally

```
pip install -r requirements.txt
streamlit run app.py
```

Create `.streamlit/secrets.toml` (never commit it):

```toml
GEMINI_API_KEY = "your-gemini-key"

[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "a-long-random-string"
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[supabase]
url = "your-supabase-url"
key = "your-supabase-secret-key"
```

Without the `[auth]` and `[supabase]` sections the app still runs, without sign-in and saved chats. Saving chats needs three Supabase tables (`conversations`, `usage_log`, `feedback`) and a `bump_usage` function.

## Limitations

- Not an official university service. Answers outside the verified facts come from an AI and can be wrong.
- Live Google Search is not available on the free Gemini quota, so the assistant cannot check current news.
- The free hosting and free Gemini quota limit how many people can use it at once.

## Author

Daksh Dhyani, BCA (Data Science), Chandigarh University. [GitHub](https://github.com/Daksh-Dhyani)