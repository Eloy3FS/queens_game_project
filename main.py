# main.py

from flask import Flask, render_template, request, jsonify
from app.controllers.game_controller import GameController
from app.models.resoution import SolverState

# Initialize Flask app
app = Flask(
    __name__,
    template_folder="app/views/templates",
    static_folder="app/views/static"
)

# Global controller: tablero 5×5 por defecto
controller = GameController(board_size=5)

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        board_size=controller.board_size,
        initial_state=controller.get_game_state()
    )

@app.route("/move", methods=["POST"])
def move():
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

@app.route("/get_time", methods=["GET"])
def get_time():
    return jsonify({
        "elapsed_time": controller.get_elapsed_time()
    })

@app.route("/reset", methods=["POST"])
def reset():
    global controller
    data = request.get_json()
    new_size = int(data.get("board_size", controller.board_size))
    if new_size < 4 or new_size > 15:
        return jsonify({"error": "Invalid board size. Must be between 4 and 15."}), 400
    controller = GameController(board_size=new_size)
    return jsonify({"state": controller.get_game_state()})

@app.route("/hint", methods=["GET"])
def hint():
    """
    Devuelve las celdas implicadas en el siguiente paso lógico
    para que el cliente las resalte.
    """
    n = controller.board_size
    solver = SolverState(controller.colored_board)

    # Aplicar estado actual del usuario al solver
    for r in range(n):
        for c in range(n):
            cell = controller.user_board[r][c]
            if cell == 'X':
                solver.candidates[r][c] = False
            elif cell == 'Q':
                solver.place_queen(r, c)

    # Probar cada paso hasta que uno cambie el estado
    for step in (
        solver.step1, solver.step2, solver.step3,
        solver.step4, solver.step5, solver.step6
    ):
        before_cand = [row[:] for row in solver.candidates]
        before_queens = [row[:] for row in solver.queens]
        changed = step()
        if changed:
            hints = []
            # Si se coloca una reina
            if step in (solver.step1, solver.step2):
                for r in range(n):
                    for c in range(n):
                        if not before_queens[r][c] and solver.queens[r][c]:
                            hints.append({"row": r, "col": c})
            else:
                # Si se eliminan candidatos → cruces
                for r in range(n):
                    for c in range(n):
                        if before_cand[r][c] and not solver.candidates[r][c]:
                            hints.append({"row": r, "col": c})
            return jsonify({"hints": hints})

    # Si ningún paso aplica, no hay hint
    return jsonify({"hints": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
