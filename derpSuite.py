from flask import Flask, request, send_from_directory, render_template
from flask_socketio import SocketIO
import frida

session = None

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route("/")
def index():
  return render_template("Index.html") 

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@app.route('/images/<path:path>')
def send_image(path):
    return send_from_directory('static/images', path)

@socketio.on('connection')
def handle_message(message):
    session = frida.get_usb_device()
    process_names = map(lambda x: x.name, session.enumerate_processes())
    return {"device": {"id": session.id, "name": session.name} , "processes": process_names}

@socketio.on("connect")
def on_connect():
    print "Client connection"

if __name__ == "__main__":
   socketio.run(app) 
