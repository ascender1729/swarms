from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/tool_b", methods=["POST"])
def tool_b():
    data = request.json
    return jsonify({"result": f"tool_b executed with {data}"}), 200


if __name__ == "__main__":
    app.run(port=5002)
