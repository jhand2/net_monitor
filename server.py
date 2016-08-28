import flask
import monitor
import threading
import atexit

app = flask.Flask(__name__)

thread = threading.Thread(target=monitor.listen)
thread.start()


@app.route("/")
def hello():
    res = {
        "msg": "Hello world",
        "app": __name__
    }
    return flask.jsonify(res)

if __name__ == "__main__":
    app.run()
