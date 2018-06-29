from flask import Flask, request, send_from_directory, render_template
from flask_socketio import SocketIO
import frida
import device

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
    return {"device": {"id": device.id(), "name": device.name()} , "processes": device.enum_processes()}

@socketio.on("process-list")
def handle_classes(message):
   print "!!!!!!!!!!!!XXXXXXXXXXXXXXXXXXXXXX!!!!!!!!!!!!!!!!!!!!!!!!!"
   return  device.enum_classes(message)

@socketio.on("class-list")
def handle_methods(message):
   print "!!!!!!!!!!!!XXXXXXXXXXXXXXXXXXXXXX!!!!!!!!!!!!!!!!!!!!!!!!!"
   return  device.enum_methods(message)

@socketio.on("connect")
def on_connect():
    print "Client connection"

@socketio.on("intercept")
def on_intercept(message):
    print "Intercept Requested: %s " % message
    method = ""
    if "method" in message:
        method = message["method"]

    device.intercept(message["class"], method, socketio)

@socketio.on("stop-intercept")
def on_stop():
    device.stop_intercept()

@socketio.on("resume-intercept")
def on_resume():
    device.resume_intercept()


@socketio.on("toggle-intercept")
def on_toggle():
    device.toggle_intercept()

@socketio.on("toggle-intercept-response")
def on_toggle_ret():
    print "Response Incercept Toggle"
    device.toggle_ret_intercept()

@socketio.on("edit-args")
def on_edit(message):
    device.send_response(message, "edit-args")

@socketio.on("edit-result")
def on_edit_result(message):
    print "[+] Edit result with: %s" % message
    device.send_response(message, "edit-result")

if __name__ == "__main__":
   socketio.run(app) 
