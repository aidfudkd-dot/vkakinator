from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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


class SessionRequest(BaseModel):
    session_id: str


games = {}

@app.post("/start_game")
async def start_game():
    try:
        aki = akinator.AsyncAkinator()
        await aki.start_game(language="russian")
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
        if user_input == "back":
            await aki.back()
        else:
            await aki.answer(user_input)
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
async def back(request: SessionRequest):
    session_id = request.session_id
    if session_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    try:
        aki = games[session_id]
        await aki.back()
        return {
            "question": str(aki),
            "progression": aki.progression,
            "step": aki.step
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
