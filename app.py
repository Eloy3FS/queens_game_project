# app.py

from flask import Flask, render_template, request, jsonify
from app.controllers.game_controller import GameController

# Initialize Flask app, pointing to your custom templates and static folders
app = Flask(
    __name__,
    template_folder="app/views/templates",
    static_folder="app/views/static"
)

# Create a single global GameController instance
# (you could also scope this per-session if you want multiple simultaneous users)
controller = GameController(board_size=8)

@app.route("/", methods=["GET"])
def index():
    """
    Render the main game page.
    Pass in the initial board size and the current game state as JSON.
    """
    return render_template(
        "index.html",
        board_size=controller.board_size,
        initial_state=controller.get_game_state()
    )

@app.route("/move", methods=["POST"])
def move():
    """
    Handle a move request from the client.
    Expects JSON with { row, col, move_type }.
    Returns JSON with { valid, message, state }.
    """
    data = request.get_json()
    row = int(data.get("row", -1))
    col = int(data.get("col", -1))
    move_type = data.get("move_type", "queen")

    valid, message = controller.update_move(row, col, move_type)
    state = controller.get_game_state()

    return jsonify({
        "valid": valid,
        "message": message,
        "state": state
    })

@app.route("/reset", methods=["POST"])
def reset():
    global controller
    data = request.get_json()
    new_size = int(data.get("board_size", controller.board_size))
    controller = GameController(board_size=new_size)
    return jsonify({ "state": controller.get_game_state() })


if __name__ == "__main__":
    # Run in debug mode on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
