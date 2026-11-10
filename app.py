import streamlit as st

from src.chatbot import FAQ_FILE, build_model, get_answer, load_faq

st.set_page_config(page_title="Student Helpdesk Chatbot", page_icon="🎓")
st.title("🎓 Student Helpdesk Chatbot")
st.caption("Ask about exams, attendance, fees or the library.")


@st.cache_resource
def load_bot():
    """Load the FAQ and build the matching model once, not on every message."""
    faq = load_faq(FAQ_FILE)
    vectorizer, question_vectors = build_model(faq)
    topics = sorted({row["topic"] for row in faq if row["topic"] not in ("about", "help")})
    return faq, vectorizer, question_vectors, ", ".join(topics)


faq, vectorizer, question_vectors, topics_text = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hello! Ask me about {topics_text}."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Type your question here")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    answer, score = get_answer(question, faq, vectorizer, question_vectors)
    if answer is None:
        answer = f"Sorry, I don't know that. Try asking about {topics_text}."
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.write(answer)