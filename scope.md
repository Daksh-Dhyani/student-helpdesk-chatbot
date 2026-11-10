# Chatbot scope

A standalone FAQ chatbot for college students. It answers from a knowledge
base I write myself (about 30 question-and-answer pairs). No external data,
no API, no connection to any other project.

## Topics (edit as you like)
- Exams and results
- Attendance rules
- Fees and scholarships
- Library
- Hostel and transport
- Contacts for departments

## How it works
1. I type a question.
2. The bot finds the closest matching question in the knowledge base.
3. It replies with the stored answer. If the match is weak, it says it does
   not know and suggests topics.

## Versions
- Version 1: keyword matching
- Version 2: smarter matching with TF-IDF (still free, no API)
- Version 3 (optional, later): an AI model for free-form questions