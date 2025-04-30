import mimetypes
from flask import Flask, render_template, request, jsonify

from app.controllers.game_controller import GameController
from app.models.resoution        import SolverState

# ─── Ensure .js/.css are served with the correct MIME ───
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app = Flask(
    __name__,
    template_folder="app/views/templates",
    static_folder="app/views/static"
)

# ─── Disable static caching in development ───
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def force_static_mime(response):
    path = request.path.lower()
    if path.endswith('.js'):
        response.headers['Content-Type'] = 'application/javascript'
    elif path.endswith('.css'):
        response.headers['Content-Type'] = 'text/css'
    return response

# ----------------------------------------------------------------------------
# Global GameController instance
# ----------------------------------------------------------------------------
controller = GameController(board_size=5, gen_mode="random")

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        board_size    = controller.board_size,
        gen_mode      = controller.gen_mode,
        initial_state = controller.get_game_state()
    )

@app.route("/move", methods=["POST"])
def move():
    data      = request.get_json()
    row       = int(data.get("row", -1))
    col       = int(data.get("col", -1))
    move_type = data.get("move_type", "queen")

    valid, message = controller.update_move(row, col, move_type)
    return jsonify({
        "valid":   valid,
        "message": message,
        "state":   controller.get_game_state()
    })

@app.route("/get_time", methods=["GET"])
def get_time():
    return jsonify({"elapsed_time": controller.get_elapsed_time()})

@app.route("/reset", methods=["POST"])
def reset():
    global controller
    data     = request.get_json()
    new_size = int(data.get("board_size", controller.board_size))
    new_mode = data.get("gen_mode",    controller.gen_mode)

    if new_size < 4 or new_size > 15:
        return jsonify({"error": "Board size must be between 4 and 15"}), 400

    controller = GameController(board_size=new_size, gen_mode=new_mode)
    return jsonify({"state": controller.get_game_state()})

@app.route("/hint", methods=["GET"])
def hint():
    n      = controller.board_size
    solver = SolverState(controller.colored_board)

    # Seed solver with current userBoard
    for r in range(n):
        for c in range(n):
            cell = controller.user_board[r][c]
            if cell == 'X':
                solver.candidates[r][c] = False
            elif cell == 'Q':
                solver.place_queen(r, c)

    # Run each hint step until something changes
    for step in (
        solver.step1, solver.step2, solver.step3,
        solver.step4, solver.step5_and_6
    ):
        before_cand   = [row[:] for row in solver.candidates]
        before_queens = [row[:] for row in solver.queens]
        if step():
            hints = []
            if step in (solver.step1, solver.step2):
                for r in range(n):
                  for c in range(n):
                    if not before_queens[r][c] and solver.queens[r][c]:
                      hints.append({"row": r, "col": c})
            else:
                for r in range(n):
                  for c in range(n):
                    if before_cand[r][c] and not solver.candidates[r][c]:
                      hints.append({"row": r, "col": c})
            return jsonify({"hints": hints})

    return jsonify({"hints": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
