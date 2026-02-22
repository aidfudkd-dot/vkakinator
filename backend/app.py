from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Dict, Any, Optional
import time
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
    step: Optional[int] = None


class SessionRequest(BaseModel):
    session_id: str


games: Dict[str, Dict[str, Any]] = {}
BROWSER_PROFILE = {"browser": "firefox", "platform": "windows", "mobile": False}
GAME_TTL_SECONDS = 30 * 60
START_ATTEMPTS = 3
START_RETRY_DELAY_SECONDS = 0.35
_last_cleanup_at = 0.0


def _state_payload(aki: akinator.Akinator) -> Dict[str, Any]:
    return {
        "finished": False,
        "question": str(aki),
        "progression": aki.progression,
        "step": aki.step,
    }


def _now() -> float:
    return time.monotonic()


def _cleanup_games_if_needed() -> None:
    global _last_cleanup_at
    now = _now()
    if now - _last_cleanup_at < 30:
        return
    expired_ids = [session_id for session_id, game in games.items() if now - game["updated_at"] > GAME_TTL_SECONDS]
    for session_id in expired_ids:
        games.pop(session_id, None)
    _last_cleanup_at = now


def _get_game(session_id: str) -> Dict[str, Any]:
    _cleanup_games_if_needed()
    game = games.get(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    game["updated_at"] = _now()
    return game


def _build_client() -> akinator.Akinator:
    session = cloudscraper.create_scraper(browser=BROWSER_PROFILE)
    return akinator.Akinator(session=session)


async def _start_game_with_retries(*, language: str = "russian", attempts: int = START_ATTEMPTS) -> akinator.Akinator:
    last_error = None
    for attempt in range(1, attempts + 1):
        aki = _build_client()
        try:
            await asyncio.to_thread(aki.start_game, language=language)
            return aki
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                await asyncio.sleep(START_RETRY_DELAY_SECONDS * attempt)
    raise RuntimeError("Failed to start the game after retries.") from last_error


def _error_detail(exc: Exception) -> str:
    cause = getattr(exc, "__cause__", None)
    if cause:
        return f"{exc} Cause: {cause}"
    return str(exc)

@app.post("/start_game")
async def start_game():
    try:
        _cleanup_games_if_needed()
        aki = await _start_game_with_retries(language="russian")
        session_id = aki.session_id
        games[session_id] = {"aki": aki, "updated_at": _now()}
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
    try:
        game = _get_game(session_id)
        aki = game["aki"]

        # Drop stale requests (e.g., double-clicks) instead of sending extra calls to Akinator.
        if request.step is not None and request.step != aki.step:
            return _state_payload(aki)

        if user_input == "back":
            await asyncio.to_thread(aki.back)
        else:
            await asyncio.to_thread(aki.answer, user_input)

        game["updated_at"] = _now()
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
            return _state_payload(aki)
    except Exception as e:
        raise HTTPException(status_code=500, detail=_error_detail(e))

@app.post("/back")
async def back(request: SessionRequest):
    session_id = request.session_id
    try:
        game = _get_game(session_id)
        aki = game["aki"]
        await asyncio.to_thread(aki.back)
        game["updated_at"] = _now()
        return _state_payload(aki)
    except Exception as e:
        raise HTTPException(status_code=500, detail=_error_detail(e))
