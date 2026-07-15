"""
Flask Application for AI-Powered Spam Detection.
Provides REST API endpoints for spam prediction and health monitoring.
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from predict import SpamPredictor
from dotenv import load_dotenv
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize predictor
predictor = None
start_time = time.time()


def get_predictor():
    global predictor
    if predictor is None:
        try:
            predictor = SpamPredictor()
        except Exception as e:
            print(f'Error loading model: {e}')
            return None
    return predictor


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    pred = get_predictor()
    model_info = pred.get_model_info() if pred else {}
    return jsonify({
        'status': 'healthy' if pred and pred.is_model_loaded() else 'model not loaded',
        'model_loaded': pred.is_model_loaded() if pred else False,
        'uptime_seconds': round(time.time() - start_time, 2),
        'model_info': model_info,
        'version': '1.0.0'
    })


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing "message" field in request body'}), 400

        message = data['message'].strip()
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        if len(message) > 10000:
            return jsonify({'error': 'Message too long. Maximum 10000 characters.'}), 400

        pred = get_predictor()
        if not pred:
            return jsonify({'error': 'Model not loaded. Please train the model first.'}), 503

        result = pred.predict(message)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
