from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variables to store the latest data and predictions
latest_data = []
latest_predictions = []

@app.route('/update_data', methods=['POST'])
def update_data():
    global latest_data
    new_data = request.json  
    print("Received data:", new_data)
    if len(latest_data) >= 2:
        latest_data.pop(0)  # Keep only the last two entries
    latest_data.append(new_data)
    return jsonify({"status": "success"}), 200

@app.route('/update_prediction', methods=['POST'])
def update_prediction():
    global latest_predictions
    new_prediction = request.json
    print("Received prediction:", new_prediction)
    if len(latest_predictions) >= 2:
        latest_predictions.pop(0)  # Keep only the last two entries
    latest_predictions.append(new_prediction)
    return jsonify({"status": "success"}), 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(latest_data)

@app.route('/predictions', methods=['GET'])
def get_predictions():
    return jsonify(latest_predictions)

if __name__ == "__main__":
    app.run(debug=True)
