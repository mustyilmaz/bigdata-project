from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Global variable to store the latest data
latest_data = []

@app.route('/update_data', methods=['POST'])
def update_data():
    global latest_data
    new_data = request.json
    print("Received data:", new_data)
    if len(latest_data) >= 2:
        latest_data.pop(0)  # Keep only the last two entries
    latest_data.append(new_data)
    return jsonify({"status": "success"}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data',  methods=['GET'])
def get_data():
    return jsonify(latest_data)

if __name__ == "__main__":
    app.run(debug=False)
