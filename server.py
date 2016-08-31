import flask
from flask import request
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient('localhost', 27017)
db = client.test

app = flask.Flask(__name__)


@app.route("/")
def hello():
    res = {
        "msg": "Hello world",
        "app": __name__
    }
    return flask.jsonify(res)


@app.route("/api/stats")
def get_last_minute():
    minutes = request.args.get("minutes") or 1
    col = db.sec_stats
    cursor = col.find(sort=[('$natural', -1)])
    docs = []
    for doc in cursor:
        if not docs:
            most_recent = doc["end_time"]
        elif most_recent - (60 * float(minutes) * 1000) > doc["start_time"]:
            break
        docs.append(doc)
    return dumps(map(remove_id, docs))


def remove_id(d):
    del d["_id"]
    return d

if __name__ == "__main__":
    app.run()
