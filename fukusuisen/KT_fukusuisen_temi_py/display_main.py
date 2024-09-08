import requests
from flask import Flask, request, jsonify
import logging
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

global_id = None

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def index():
    return "A"


@app.route('/set_id', methods=['POST'])
def set_id_route():
    global global_id
    try:
        data = request.get_json()
        app.logger.debug(f"Received data: {data}")
        id = data.get('id')
        if id is not None:
            global_id = id
            app.logger.debug(f"ID set to: {id}")
            return jsonify({"message": "ID set successfully"}), 200
        else:
            app.logger.debug("No ID provided")
            return jsonify({"error": "No ID provided"}), 400
    except Exception as e:
        app.logger.debug(f"Error: {e}")
        return jsonify({"error": "Bad Request"}), 400


@app.route('/process_id', methods=['GET'])
def process_id():
    global global_id
    if global_id is None:
        app.logger.debug("ID not set")
        return jsonify({"error": "ID not set"}), 400

    id = global_id

    if id == 70:
        app.logger.debug("70です")
    elif id == 71:
        app.logger.debug("71です")
    elif 1 <= id <= 32:
        server_url = 'http://localhost:5001/update_image'
        app.logger.debug("1から32です")
    elif 33 <= id <= 66:
        server_url = 'http://localhost:5002/update_image'
        app.logger.debug("33から66です")
    else:
        server_url = 'http://localhost:5003/update_image'
        app.logger.debug("67から100です")

    image_src = f'static/images/{id}.jpg'
    response = requests.post(server_url, json={'image_src': image_src})
    if response.status_code == 200:
        app.logger.debug(f"Image updated on server: {server_url}")
        return jsonify({"message": f"Image updated on server: {server_url}"})
    else:
        app.logger.debug(f"Failed to update image on server: {server_url}")
        return jsonify({"message": f"Failed to update image on server: {server_url}"}), 500


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4999, allow_unsafe_werkzeug=True)
