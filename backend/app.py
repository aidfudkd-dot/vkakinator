from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from akinator.async_client import AsyncClient
from pydantic import BaseModel
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

games = {}

@app.post("/start_game")
async def start_game():
    client = AsyncClient()
    await client.start_game(language="russian", theme="c")
    session_id = client.session_id
    games[session_id] = client
    return {
        "session_id": session_id,
        "question": client.question,
        "progression": client.progression,
        "step": client.step
    }

@app.post("/answer")
async def answer(request: AnswerRequest):
    session_id = request.session_id
    if session_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    client = games[session_id]
    await client.answer(request.answer)
    if client.win:
        return {
            "finished": True,
            "name_proposition": client.name_proposition,
            "description_proposition": client.description_proposition,
            "pseudo": client.pseudo,
            "photo": client.photo,
            "final_message": "Great, guessed right one more time !"
        }
    else:
        return {
            "finished": False,
            "question": client.question,
            "progression": client.progression,
            "step": client.step
        }

@app.post("/back")
async def back(session_id: str):
    if session_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    client = games[session_id]
    await client.back()
    return {
        "question": client.question,
        "progression": client.progression,
        "step": client.step
    }