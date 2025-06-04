from flask import Flask, request, jsonify
import pickle
from graph_utils import load_data, find_degrees

app = Flask(__name__)

people = None
names = None
graph = None

@app.route("/degrees", methods=["POST"])
def degrees():
    data = request.json
    source = data.get("source")
    target = data.get("target")

    if not source or not target:
        return jsonify({"error": "Please provide source and target names"}), 400

    result = find_degrees(graph, people, names, source, target)
    if result["error"]:
        return jsonify(result), 404
    return jsonify(result)

if __name__ == "__main__":
    print("Loading data...")
    people, names = load_data()
    print("Loading graph...")
    with open("graph.pkl", "rb") as f:
        graph = pickle.load(f)
    print("Starting server...")
    app.run(debug=True)
