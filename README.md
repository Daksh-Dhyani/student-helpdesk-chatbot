# Student Helpdesk Chatbot

**Live demo:** https://student-appdesk-chatbot-ndgowicfzdsfnecwqjibra.streamlit.app/

An AI helpdesk assistant for university students, built in Python with
Streamlit. It answers questions about my own university from a knowledge base
I wrote and verified myself, and it can also answer general questions like a
normal AI assistant.

> Not an official university service. General answers come from an AI and can
> be wrong. University answers come only from the verified facts in
> `data/faq.csv`.

## Features
- Web chat page with a typing effect and example questions in the sidebar
- Time-based greeting (Good morning / afternoon / evening, Indian time)
- Short chat memory, so follow-up questions make sense
- Verified answers on academics, attendance, exams, fees, hostel, library,
  offices, scholarships and transport
- General questions (coding, study help, advice) answered by a Google Gemini
  model
- If the AI is busy or unavailable, it falls back to simple matching on the
  verified answers and says so
- Study helper: upload a syllabus (PDF or text) and get explanations, a 7-day
  study plan, practice questions or revision notes based on it. The file is
  used only for the current chat.

## How it works
1. **Verified facts:** `data/faq.csv` holds questions, answers and keywords.
2. **AI layer:** the Gemini model receives the verified facts with strict
   instructions: for university questions, answer only from those facts and
   say "not sure" if the answer is not there. Other questions are answered
   freely.
3. **Fallback layer:** if the AI call fails, TF-IDF and cosine similarity
   (scikit-learn) find the closest stored question. Weak matches are
   rejected, so the bot does not give a wrong answer.

## Project structure
```
student-helpdesk-chatbot/
├── app.py              Streamlit web app (AI layer and chat page)
├── src/chatbot.py      rules-based matching (TF-IDF) and terminal version
├── data/faq.csv        verified questions, answers and keywords
├── requirements.txt
└── README.md
```

## Run it locally
1. Create and activate a virtual environment, then
   `pip install -r requirements.txt`
2. Create `.streamlit/secrets.toml` with your own Gemini API key:
   ```
   GEMINI_API_KEY = "your-key-here"
   ```
   Never commit this file. It is listed in `.gitignore`.
3. Run `streamlit run app.py`

Without a key the app still works in rules-only mode.

## Add or change answers
Edit `data/faq.csv`. Each row is `topic,question,answer,keywords`. Put
answers that contain commas inside double quotes. Add the words students
might actually type to the keywords column.

## Limitations
- Answers reflect what I know about my university and may be out of date.
  Confirm important details with the college office or CUIMS.
- General AI answers are not verified and can be wrong.
- The AI runs on a free Gemini plan, so it can be slow or busy at times.
- The rules fallback matches words, not meaning.
- Scanned or photographed PDFs can't be read, only text-based ones.
- Practice questions are guesses, not the real exam paper.

## Author
Daksh Dhyani, BCA Data Science (Hons.), Chandigarh University