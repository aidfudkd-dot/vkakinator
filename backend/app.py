from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'akinator.py'))

from akinator.async_client import AsyncClient
import asyncio

app = Flask(__name__)
CORS(app)

games = {}

@app.route('/start_game', methods=['POST'])
def start_game():
    client = AsyncClient()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start_game(language="russian", theme="c"))
    session_id = client.session_id
    games[session_id] = client
    return jsonify({
        "session_id": session_id,
        "question": client.question,
        "progression": client.progression,
        "step": client.step
    })

@app.route('/answer', methods=['POST'])
def answer():
    data = request.json
    session_id = data['session_id']
    answer = data['answer']
    if session_id not in games:
        return jsonify({"error": "Game not found"}), 404
    client = games[session_id]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.answer(answer))
    if client.win:
        return jsonify({
            "finished": True,
            "name_proposition": client.name_proposition,
            "description_proposition": client.description_proposition,
            "pseudo": client.pseudo,
            "photo": client.photo,
            "final_message": "Great, guessed right one more time !"
        })
    else:
        return jsonify({
            "finished": False,
            "question": client.question,
            "progression": client.progression,
            "step": client.step
        })

@app.route('/back', methods=['POST'])
def back():
    data = request.json
    session_id = data['session_id']
    if session_id not in games:
        return jsonify({"error": "Game not found"}), 404
    client = games[session_id]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.back())
    return jsonify({
        "question": client.question,
        "progression": client.progression,
        "step": client.step
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)