from flask import Flask, render_template, request, jsonify
from game import GameLogic

app = Flask(__name__)
game_logic = GameLogic()

@app.route("/")
def index():
    game_state = game_logic.get_game_state()
    return render_template("index.html", grid_size=8, cell_color=game_state["cell_colors"],
                           message=game_state["message"])

@app.route("/new_game", methods=["POST"])
def new_game():
    response = game_logic.new_game()
    return jsonify(response)

@app.route("/toggle_safe_mode", methods=["POST"])
def toggle_safe_mode():
    response = game_logic.toggle_safe_mode()
    return jsonify(response)

@app.route("/reset_game", methods=["POST"])
def reset_game():
    response = game_logic.reset_game()
    return jsonify(response)

@app.route("/move_agent", methods=["POST"])
def move_agent():
    direction = request.json.get("direction")
    response = game_logic.move_agent(direction)
    return jsonify(response)

@app.route("/check_cell", methods=["POST"])
def check_cell():
    data = request.json
    x, y = data.get("x"), data.get("y")
    response = game_logic.handle_double_click(x, y)
    return jsonify(response)

@app.route("/reveal_answer", methods=["POST"])
def reveal_answer():
    response = game_logic.reveal_answer()
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=False)
