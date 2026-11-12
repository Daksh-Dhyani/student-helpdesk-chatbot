import re
import time
from datetime import datetime, timedelta, timezone

import streamlit as st

from src.chatbot import FAQ_FILE, build_model, get_answer, load_faq

# Check the current model name in Google AI Studio if this one stops working.
MODEL_NAMES = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite"]
GREETINGS = {"hi", "hello", "hey", "hii", "hy", "hlo", "hola"}
IST = timezone(timedelta(hours=5, minutes=30))
TYPING_DELAY = 0.03  # seconds per word; make it smaller for faster typing

st.set_page_config(page_title="Student Helpdesk Chatbot", page_icon="🎓")


def time_greeting():
    hour = datetime.now(IST).hour
    if 5 <= hour < 12:
        return "Good morning"
    if 12 <= hour < 17:
        return "Good afternoon"
    if 17 <= hour < 21:
        return "Good evening"
    return "Hello"


@st.cache_resource
def load_bot():
    faq = load_faq(FAQ_FILE)
    vectorizer, question_vectors = build_model(faq)
    topics = sorted({row["topic"] for row in faq} - {"about", "help"})
    return faq, vectorizer, question_vectors, topics


@st.cache_resource
def load_client():
    try:
        key = st.secrets["GEMINI_API_KEY"]
        from google import genai
        from google.genai import types
        return genai.Client(
            api_key=key,
            http_options=types.HttpOptions(
                timeout=20000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
    except Exception:
        return None


def word_stream(text):
    """Yield a finished text one word at a time (typing effect)."""
    for word in re.findall(r"\s*\S+\s*|\s+", text):
        yield word
        time.sleep(TYPING_DELAY)


def build_prompt(faq, history, question):
    knowledge = "\n".join(
        f"- Q: {row['question']}\n  A: {row['answer']}" for row in faq
    )
    chat = "\n".join(f"{m['role']}: {m['content']}" for m in history[-6:])
    return (
        "You are a friendly, helpful AI assistant for university students. "
        "You can answer any question: studies, coding, general knowledge, "
        "advice, and everyday doubts. Keep replies clear and not too long, "
        "and reply in the same language style the student uses.\n\n"
        "STRICT RULE FOR UNIVERSITY QUESTIONS: if the student asks about "
        "their own university (hostel, fees, exams, attendance, library, "
        "transport, scholarships, offices, rules, dates, places, people), "
        "answer ONLY from the verified facts below. Never invent or guess "
        "any university detail. If the facts do not contain it, say you are "
        "not sure and suggest asking the college office or checking CUIMS.\n"
        f"If the student greets you, greet back with '{time_greeting()}'.\n\n"
        f"VERIFIED UNIVERSITY FACTS:\n{knowledge}\n\n"
        f"CHAT SO FAR:\n{chat}\n\n"
        f"STUDENT: {question[:500]}\nASSISTANT:"
    )


def ai_stream(client, faq, history, question):
    """Yield the AI reply word by word. Tries each model if one is busy."""
    prompt = build_prompt(faq, history, question)
    last_error = None
    for model in MODEL_NAMES:
        for attempt in range(1):
            started = False
            try:
                for chunk in client.models.generate_content_stream(
                    model=model, contents=prompt
                ):
                    if chunk.text:
                        started = True
                        yield from word_stream(chunk.text)
                return
            except Exception as e:
                if started:
                    raise
                last_error = e
                time.sleep(2)
    raise last_error


faq, vectorizer, question_vectors, topics = load_bot()
client = load_client()
topics_text = ", ".join(topics)
welcome = (time_greeting() + "! 👋 I'm your helpdesk assistant. Ask me about "
           + topics_text + ".")

# ---- Sidebar ----
with st.sidebar:
    st.header("🎓 Helpdesk")
    st.write("**Topics:** " + topics_text)
    st.write("**Mode:** " + ("AI assistant + verified university facts" if client else "Rules only"))
    st.divider()
    st.write("Try asking:")
    for q in ["When do exams start?", "What attendance is required?",
              "How can I pay my fees?", "What are the library timings?"]:
        if st.button(q, use_container_width=True):
            st.session_state.pending = q
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Not an official university service. University answers come "
               "from verified facts. General answers come from an AI and can "
               "be wrong, so double-check anything important.")

# ---- Main page ----
st.title("🎓 Student Helpdesk Chatbot")
st.caption("Ask about " + topics_text + ".")

if "messages" not in st.session_state:
    st.session_state.messages = []
if not st.session_state.messages:
    st.session_state.messages.append(
        {"role": "assistant", "content": welcome, "source": ""}
    )

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("source"):
            st.caption(m["source"])

typed = st.chat_input("Type your question here")
question = st.session_state.pop("pending", None) or typed

if question:
    history = list(st.session_state.messages)
    st.session_state.messages.append(
        {"role": "user", "content": question, "source": ""}
    )
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        answer, source = None, "answered by rules"

        if client is not None:
            try:
                answer = st.write_stream(ai_stream(client, faq, history, question))
                source = "answered by AI (university facts are verified, general answers are not)"
            except Exception as e:
                answer = None  # fall back to rules if the AI call fails
                st.warning(f"AI unavailable: {type(e).__name__}: {str(e)[:200]}")

        if not answer:
            source = "answered by rules"
            if question.lower().strip() in GREETINGS:
                text = welcome
            else:
                found, _score = get_answer(
                    question, faq, vectorizer, question_vectors
                )
                text = found or ("Sorry, I don't know that. Try asking about "
                                 + topics_text + ".")
            answer = st.write_stream(word_stream(text))

        st.caption(source)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "source": source}
    )