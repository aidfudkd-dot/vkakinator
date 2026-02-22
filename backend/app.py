from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import akinator
import cloudscraper

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
BROWSER_PROFILE = {"browser": "firefox", "platform": "windows", "mobile": False}


def _build_client() -> akinator.Akinator:
    session = cloudscraper.create_scraper(browser=BROWSER_PROFILE)
    return akinator.Akinator(session=session)


async def _start_game_with_retries(*, language: str = "russian", attempts: int = 3) -> akinator.Akinator:
    last_error = None
    for _ in range(attempts):
        aki = _build_client()
        try:
            await asyncio.to_thread(aki.start_game, language=language)
            return aki
        except Exception as exc:
            last_error = exc
    raise RuntimeError("Failed to start the game after retries.") from last_error


def _error_detail(exc: Exception) -> str:
    cause = getattr(exc, "__cause__", None)
    if cause:
        return f"{exc} Cause: {cause}"
    return str(exc)

@app.post("/start_game")
async def start_game():
    try:
        aki = await _start_game_with_retries(language="russian")
        session_id = aki.session_id
        games[session_id] = aki
        return {
            "session_id": session_id,
            "question": str(aki),
            "progression": aki.progression,
            "step": aki.step
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=_error_detail(e))

@app.post("/answer")
async def answer(request: AnswerRequest):
    session_id = request.session_id
    user_input = request.answer
    if session_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    try:
        aki = games[session_id]
        if user_input == "back":
            await asyncio.to_thread(aki.back)
        else:
            await asyncio.to_thread(aki.answer, user_input)
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
        raise HTTPException(status_code=500, detail=_error_detail(e))

@app.post("/back")
async def back(request: SessionRequest):
    session_id = request.session_id
    if session_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    try:
        aki = games[session_id]
        await asyncio.to_thread(aki.back)
        return {
            "question": str(aki),
            "progression": aki.progression,
            "step": aki.step
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=_error_detail(e))
