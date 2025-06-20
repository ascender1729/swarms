from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/tool_a", methods=["POST"])
def tool_a():
    data = request.json
    return jsonify({"result": f"tool_a executed with {data}"}), 200


if __name__ == "__main__":
    app.run(port=5001)
