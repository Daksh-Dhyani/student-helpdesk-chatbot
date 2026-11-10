# Student Helpdesk Chatbot

**Live demo:** https://student-appdesk-chatbot-ndgowicfzdsfnecwqjibra.streamlit.app/

A small FAQ chatbot for college students, built in Python. It answers
questions about exams, attendance, fees and the library from a knowledge base
I wrote myself. No external API is used.

## How it works
1. Every stored question (plus a few keywords) is turned into a vector of
   word weights using TF-IDF (scikit-learn).
2. The user's question is converted the same way.
3. Cosine similarity finds the closest stored question.
4. If the match score is above 0.20, the bot shows that answer. Otherwise it
   says it does not know and lists the topics it can help with.

## Project structure
```
student-helpdesk-chatbot/
├── app.py              web version (Streamlit)
├── data/faq.csv        questions, answers and keywords
├── src/chatbot.py      the chatbot
├── requirements.txt
└── README.md
```

## How to run
1. Create and activate a virtual environment, then
   `pip install -r requirements.txt`
2. Run `python src/chatbot.py`
3. To run the web version instead, use `streamlit run app.py`
4. Type a question, for example `how to pay fees`. Type `quit` to exit.

## Example
```
You: exam dates
Bot: Mid-semester exams are held twice per semester. End-semester exams are held in May and December.  (match 0.38)
You: what is the weather
Bot: Sorry, I don't know that. Try asking about attendance, exams, fees, library.
```

## Limitations
- It matches words, not meaning. Different wording may not be understood
  unless the keywords column covers it. For example, `what can you do` is made
  only of filler words, so the bot does not match it (`help` works).
- It does not correct spelling mistakes by itself.
- The answers come from my own knowledge of my college and may be incomplete
  or out of date. Check with the college office for official information.

## Next steps
- Add more questions and keywords.
- Optional: connect an AI model for free-form questions.

## Author
Daksh Dhyani, BCA Data Science (Hons.), Chandigarh University