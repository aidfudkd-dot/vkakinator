from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import akinator

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
    try:
        aki = akinator.Akinator()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(aki.start_game(language="russian"))
        session_id = aki.session_id
        games[session_id] = aki
        return {
            "session_id": session_id,
            "question": str(aki),
            "progression": aki.progression,
            "step": aki.step
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/answer")
async def answer(request: AnswerRequest):
    session_id = request.session_id
    user_input = request.answer
    if session_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    try:
        aki = games[session_id]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        if user_input == "back":
            loop.run_until_complete(aki.back())
        else:
            loop.run_until_complete(aki.answer(user_input))
        if aki.finished:
            return {
                "finished": True,
                "name_proposition": aki.name_proposition,
                "description_proposition": aki.description_proposition,
                "pseudo": aki.pseudo,
                "photo": aki.photo,
                "final_message": aki.question
            }
        else:
            return {
                "finished": False,
                "question": str(aki),
                "progression": aki.progression,
                "step": aki.step
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/back")
async def back(session_id: str):
    if session_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    try:
        aki = games[session_id]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(aki.back())
        return {
            "question": str(aki),
            "progression": aki.progression,
            "step": aki.step
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))