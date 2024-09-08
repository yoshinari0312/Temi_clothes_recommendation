import sys
sys.path.append('/opt/homebrew/lib/python3.11/site-packages')
from flask_socketio import SocketIO
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('hello_socketio.html')


@app.route('/update_image', methods=['POST'])
def update_image():
    data = request.get_json()
    image_src = data['image_src']
    socketio.emit('update_image', {'image_src': image_src})
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
