import csv
from pathlib import Path

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FAQ_FILE = Path(__file__).parent.parent / "data" / "faq.csv"
MIN_SCORE = 0.20      # below this, the bot says it does not know
SHOW_SCORE = True     # print the match score so we can learn from it

# scikit-learn's list of filler words, but we keep "made" (as in "who made you")
STOP_WORDS = list(ENGLISH_STOP_WORDS - {"made"})


def load_faq(path):
    """Read faq.csv and skip any row whose answer is still 'FILL IN'."""
    with open(path, encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    return [row for row in rows if row["answer"].strip() != "FILL IN"]


def build_model(faq):
    """Turn each stored question plus its keywords into TF-IDF vectors."""
    texts = [row["question"] + " " + row["keywords"] for row in faq]
    vectorizer = TfidfVectorizer(lowercase=True, stop_words=STOP_WORDS, ngram_range=(1, 1))
    question_vectors = vectorizer.fit_transform(texts)
    return vectorizer, question_vectors


def get_answer(user_text, faq, vectorizer, question_vectors):
    """Find the stored question closest to the user's text."""
    user_vector = vectorizer.transform([user_text])
    scores = cosine_similarity(user_vector, question_vectors)[0]
    best = scores.argmax()
    if scores[best] < MIN_SCORE:
        return None, scores[best]
    return faq[best]["answer"], scores[best]


def main():
    faq = load_faq(FAQ_FILE)
    vectorizer, question_vectors = build_model(faq)
    topics = sorted({row["topic"] for row in faq if row["topic"] not in ("about", "help")})
    topics_text = ", ".join(topics)

    print("Student Helpdesk Chatbot. Type 'quit' to exit.")
    while True:
        text = input("You: ").strip()
        if not text:
            continue
        if text.lower() in {"quit", "exit", "bye"}:
            print("Bot: Goodbye!")
            break
        if text.lower() in {"hi", "hello", "hey"}:
            print(f"Bot: Hello! Ask me about {topics_text}.")
            continue

        answer, score = get_answer(text, faq, vectorizer, question_vectors)
        if answer is None:
            print(f"Bot: Sorry, I don't know that. Try asking about {topics_text}.")
        elif SHOW_SCORE:
            print(f"Bot: {answer}  (match {score:.2f})")
        else:
            print(f"Bot: {answer}")


if __name__ == "__main__":
    main()