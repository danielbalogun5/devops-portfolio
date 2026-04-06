from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

DEFAULT_ITEMS = [
    "Option 1", "Option 2", "Option 3", "Option 4",
    "Option 5", "Option 6", "Option 7", "Option 8"
]


@app.route("/")
def index():
    return render_template("index.html", items=DEFAULT_ITEMS)


@app.route("/spin", methods=["POST"])
def spin():
    data = request.get_json()
    items = data.get("items", DEFAULT_ITEMS)
    if not items:
        return jsonify({"error": "No items provided"}), 400
    winner = random.choice(items)
    winner_index = items.index(winner)
    return jsonify({"winner": winner, "winner_index": winner_index})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
