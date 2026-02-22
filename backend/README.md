# Akinator Backend

This is the backend for the Akinator VK Mini App.

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Run the server:
   uvicorn app:app --host 0.0.0.0 --port 8000

## Endpoints

- POST /start_game: Start a new game
- POST /answer: Answer a question
- POST /back: Go back to previous question

## Deployment

Deploy to Render.com with the Procfile and requirements.txt.