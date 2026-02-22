from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import akinator

app = Flask(__name__)
CORS(app)

games = {}

@app.route('/start_game', methods=['POST'])
def start_game():
    aki = akinator.Akinator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(aki.start_game(language="russian"))
        session_id = aki.session_id
        games[session_id] = aki
        return jsonify({
            "session_id": session_id,
            "question": str(aki),
            "progression": aki.progression,
            "step": aki.step
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/answer', methods=['POST'])
def answer():
    data = request.json
    session_id = data['session_id']
    user_input = data['answer']
    if session_id not in games:
        return jsonify({"error": "Game not found"}), 404
    aki = games[session_id]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if user_input == "back":
            loop.run_until_complete(aki.back())
        else:
            loop.run_until_complete(aki.answer(user_input))
        if aki.finished:
            return jsonify({
                "finished": True,
                "name_proposition": aki.name_proposition,
                "description_proposition": aki.description_proposition,
                "pseudo": aki.pseudo,
                "photo": aki.photo,
                "final_message": aki.question
            })
        else:
            return jsonify({
                "finished": False,
                "question": str(aki),
                "progression": aki.progression,
                "step": aki.step
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True)