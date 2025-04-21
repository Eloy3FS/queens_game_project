from flask import Flask, render_template, request, jsonify
from app.controllers import game_controller

app = Flask(__name__)

# Ruta principal: renderiza la interfaz
@app.route("/")
def index():
    # Aquí puedes inicializar el juego o recuperar el estado actual
    # Por simplicidad, asume que en game_controller se gestiona un objeto global o sesión
    # por ahora se renderiza la plantilla con el estado inicial (a definir).
    return render_template("index.html")

# Endpoint para procesar jugadas (ej. al hacer clic en una celda)
@app.route("/move", methods=["POST"])
def move():
    data = request.get_json()
    # data debe incluir las coordenadas y el tipo de movimiento
    row = data.get("row")
    col = data.get("col")
    move_type = data.get("move_type")
    # Llama a la lógica del controlador (por ejemplo, game_controller.update_move)
    # Supongamos que game_controller tiene una función update_move que devuelve el nuevo estado y un mensaje.
    valid, message, state = game_controller.update_move(row, col, move_type)
    return jsonify({"valid": valid, "message": message, "state": state})

# Endpoint para reiniciar el juego o cambiar el tamaño del tablero
@app.route("/reset", methods=["POST"])
def reset():
    new_size = request.get_json().get("board_size")
    # Reinicia la instancia del juego en game_controller
    game_controller.reset_game(new_size)
    # Devuelve el nuevo estado de juego
    return jsonify({"state": game_controller.get_game_state()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
