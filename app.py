import html
import os
import re
import time
from datetime import datetime, timedelta, timezone
from io import BytesIO

import streamlit as st

from src.chatbot import FAQ_FILE, build_model, get_answer, load_faq

MODEL_NAMES = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.7-flash"]
GREETINGS = {"hi", "hello", "hey", "hii", "hy", "hlo", "hola"}
IST = timezone(timedelta(hours=5, minutes=30))
TYPING_DELAY = 0.01  # seconds per word; make it smaller for faster typing
MAX_QUESTION_CHARS = 4000
MAX_SYLLABUS_CHARS = 30000
MAX_HISTORY_CHARS = 1500

STUDY_PROMPTS = {
    "📖 Explain unit 1 simply": "Explain unit 1 of my syllabus simply, with examples.",
    "🗓️ 7-day study plan": "Make a 7-day study plan for my syllabus.",
    "❓ 10 practice questions": "Give me 10 likely exam-style practice questions with answers from my syllabus.",
    "📝 Short revision notes": "Make short revision notes for my syllabus.",
}

STARTERS = [
    ("🏠 Hostel in-time", "What is the hostel in time?"),
    ("📅 When do exams start?", "When do exams start?"),
    ("🚌 Bus pass", "How can I get a bus pass and find my route?"),
    ("🎓 Scholarships", "Are scholarships available?"),
]

st.set_page_config(page_title="Student Helpdesk Chatbot", page_icon="🎓")
st.markdown("""
<style>
.stApp {background: radial-gradient(circle at 20% 0%, #1b1440 0%, #0b0b14 55%);}
.block-container {padding-top: 2rem; max-width: 900px;}
.maker {
  display: inline-flex; align-items: center; gap: 6px; margin: 0 0 12px;
  padding: 5px 14px; border-radius: 999px; font-size: .85rem; color: #ddd6fe;
  background: rgba(255,255,255,.06); border: 1px solid rgba(167,139,250,.4);
  animation: rise .6s ease both;
}
.maker a {color: #c4b5fd; text-decoration: none; font-weight: 600;}
.maker a:hover {color: #ffffff; text-decoration: underline;}
.hero {
  background: linear-gradient(120deg, #4f46e5, #7c3aed, #db2777, #4f46e5);
  background-size: 300% 300%;
  animation: flow 8s ease infinite;
  border-radius: 20px; padding: 26px 30px; color: white;
  margin-bottom: 16px; box-shadow: 0 8px 30px rgba(124,58,237,.35);
}
.hero h1 {margin: 0; padding: 0; font-size: 2.1rem; color: white;}
.hero p {margin: 6px 0 0; opacity: .93; font-size: 1.02rem; color: white;}
@keyframes flow {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}
@keyframes rise {
  from {opacity: 0; transform: translateY(10px);}
  to {opacity: 1; transform: none;}
}
.chips {display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 18px;}
.chip {
  padding: 6px 14px; border-radius: 999px; font-size: .9rem;
  background: rgba(124,58,237,.18); border: 1px solid rgba(167,139,250,.4);
  animation: rise .6s ease both;
}
[data-testid="stChatMessage"] {
  background: rgba(255,255,255,.04) !important;
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 16px; animation: rise .45s ease both;
}
.stButton > button {
  border-radius: 12px; background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.12); transition: all .2s ease;
}
.stButton > button:hover {
  border-color: #a78bfa; color: #c4b5fd; transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(124,58,237,.3);
}
section[data-testid="stSidebar"] {background: rgba(10,10,24,.85);}
</style>
""", unsafe_allow_html=True)


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
def load_bot(file_stamp):
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


@st.cache_data(show_spinner=False)
def extract_text(name, data):
    """Read the text of an uploaded PDF or text file."""
    if name.lower().endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(data))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    else:
        text = data.decode("utf-8", errors="ignore")
    return text.strip()


def word_stream(text):
    """Yield a finished text one word at a time (typing effect)."""
    for word in re.findall(r"\s*\S+\s*|\s+", text):
        yield word
        time.sleep(TYPING_DELAY)


def build_prompt(faq, history, question, syllabus):
    knowledge = "\n".join(
        f"- Q: {row['question']}\n  A: {row['answer']}" for row in faq
    )
    chat = "\n".join(
        f"{m['role']}: {m['content'][:MAX_HISTORY_CHARS]}" for m in history[-6:]
    )
    syllabus_part = ""
    if syllabus:
        syllabus_part = (
            "STUDENT'S UPLOADED SYLLABUS (use it for study requests such as "
            "explaining units, study plans, revision notes and practice "
            "questions):\n" + syllabus + "\n\n"
        )
    return (
        "You are a friendly, helpful AI assistant for university students. "
        "You can answer any question: studies, coding, general knowledge, "
        "advice, and everyday doubts. Keep replies clear and well organised, "
        "and reply in the same language style the student uses. Write only "
        "in English (or Hinglish in Latin letters if the student does). Never "
        "use any other script or language unless the student writes in it. "
        "When a verified fact answers the question, keep its wording and "
        "numbers exactly.\n\n"
        "STRICT RULE FOR UNIVERSITY QUESTIONS: if the student asks about "
        "their own university (hostel, fees, exams, attendance, library, "
        "transport, scholarships, offices, rules, dates, places, people), "
        "answer ONLY from the verified facts below. Never invent or guess "
        "any university detail. If the facts do not contain it, say you are "
        "not sure and suggest asking the college office or checking CUIMS.\n"
        "For study help from the syllabus: practice questions are only "
        "guesses, not the real exam paper, so say that briefly. Never claim "
        "to know what will actually come in the student's exam.\n"
        f"If the student greets you, greet back with '{time_greeting()}'.\n\n"
        f"VERIFIED UNIVERSITY FACTS:\n{knowledge}\n\n"
        f"{syllabus_part}"
        f"CHAT SO FAR:\n{chat}\n\n"
        f"STUDENT: {question}\nASSISTANT:"
    )


def ai_stream(client, faq, history, question, syllabus):
    """Yield the AI reply word by word. Tries each model if one is busy."""
    from google.genai import types

    prompt = build_prompt(faq, history, question, syllabus)
    settings = types.GenerateContentConfig(temperature=0.3)
    last_error = None
    for model in MODEL_NAMES:
        started = False
        try:
            for chunk in client.models.generate_content_stream(
                model=model, contents=prompt, config=settings
            ):
                if chunk.text:
                    started = True
                    yield from word_stream(chunk.text)
            return
        except Exception as e:
            if started:
                raise
            last_error = e
    raise last_error


faq, vectorizer, question_vectors, topics = load_bot(os.path.getmtime(FAQ_FILE))
client = load_client()
topics_text = ", ".join(topics)
welcome = time_greeting() + "! 👋 How can I help you today?"

syllabus = ""

# ---- Sidebar ----
with st.sidebar:
    st.header("🎓 Helpdesk")
    st.caption("Built by Daksh Dhyani · BCA Data Science, Chandigarh University")
    st.write("**Topics:** " + topics_text)
    st.write("**Mode:** " + ("AI assistant + verified university facts"
                             if client else "Rules only"))
    st.divider()
    st.write("Try asking:")
    for q in ["When do exams start?", "What attendance is required?",
              "How can I pay my fees?", "What are the library timings?"]:
        if st.button(q, use_container_width=True):
            st.session_state.pending = q

    st.divider()
    st.write("📚 **Study helper**")
    uploaded = st.file_uploader(
        "Upload your syllabus (PDF or text)", type=["pdf", "txt"]
    )
    if uploaded is not None:
        try:
            file_text = extract_text(uploaded.name, uploaded.getvalue())
        except Exception:
            file_text = ""
        if file_text:
            syllabus = file_text[:MAX_SYLLABUS_CHARS]
            st.success("Syllabus loaded: " + uploaded.name)
            if len(file_text) > MAX_SYLLABUS_CHARS:
                st.caption("The file is long, so only the first part is used.")
        else:
            st.warning("I couldn't read any text from this file. Scanned "
                       "or photo PDFs don't work. Try a text PDF.")
    if syllabus:
        for label, study_prompt in STUDY_PROMPTS.items():
            if st.button(label, use_container_width=True):
                st.session_state.pending = study_prompt
    if not client:
        st.caption("Study help needs the AI, which is off right now.")

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Not an official university service. University answers come "
               "from verified facts. General and study answers come from an "
               "AI and can be wrong, so double-check anything important. An "
               "uploaded syllabus is used only for your current chat and is "
               "sent to Google's AI service. Don't upload personal documents.")

# ---- Main page ----
chips = "".join(
    f'<span class="chip">{html.escape(t.title())}</span>' for t in topics
)
st.markdown(f"""
<div class="maker">✨ Made by <a href="https://github.com/Daksh-Dhyani" target="_blank" rel="noopener">Daksh Dhyani</a></div>
<div class="hero">
<h1>🎓 Student Helpdesk</h1>
<p>Campus questions answered instantly, plus an AI study buddy.</p>
</div>
<div class="chips">{chips}</div>
""", unsafe_allow_html=True)

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

if len(st.session_state.messages) == 1 and "pending" not in st.session_state:
    st.write("**Try one of these:**")
    cols = st.columns(2)
    for i, (label, starter_text) in enumerate(STARTERS):
        if cols[i % 2].button(label, key=f"start{i}", use_container_width=True):
            st.session_state.pending = starter_text
            st.rerun()

typed = st.chat_input("Type your question here")
question = st.session_state.pop("pending", None) or typed

if question:
    question = question[:MAX_QUESTION_CHARS]
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
                answer = st.write_stream(
                    ai_stream(client, faq, history, question, syllabus)
                )
                source = "answered by AI (university facts are verified, general answers are not)"
            except Exception as e:
                answer = None  # fall back to rules if the AI call fails
                print("AI error:", type(e).__name__, str(e)[:200])

        ai_failed = client is not None and not answer

        if not answer:
            source = "answered by rules"
            if question.lower().strip() in GREETINGS:
                text = welcome
            else:
                found, score = get_answer(
                    question, faq, vectorizer, question_vectors
                )
                if ai_failed and (found is None or score < 0.35):
                    text = ("The AI is busy right now, so I can only answer "
                            "questions I have verified answers for. Please "
                            "try again in a few minutes.")
                    source = "AI temporarily unavailable"
                else:
                    text = found or ("Sorry, I don't know that. Try asking "
                                     "about " + topics_text + ".")
            answer = st.write_stream(word_stream(text))

        st.caption(source)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "source": source}
    )