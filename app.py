import datetime
import os

from flask import Flask, Response, request, jsonify
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': os.environ['MONGODB_HOST'],
    'username': os.environ['MONGODB_USERNAME'],
    'password': os.environ['MONGODB_PASSWORD'],
    'authSource': 'smart-ledger',
    'db': 'smart-ledger'
}

db = MongoEngine()
db.init_app(app)


class Person(db.Document):
    first_name = db.StringField(max_length=60, required=True)
    last_name = db.StringField(max_length=60, required=True)
    email = db.EmailField(max_length=60, required=True)
    groups = db.ListField(default=[])


class Group(db.Document):
    name = db.StringField(max_length=60, required=True)
    people = db.ListField(default=[])
    transactions = db.ListField(default=[])


@app.route("/person", methods=['GET'])
def get_person():
    email = request.args.get('email')
    person = Person.objects(email=email).first()
    return jsonify(person), 200


@app.route("/group", methods=['GET'])
def get_group():
    g_id = request.args.get('id')
    group = Group.objects(id=g_id).first()
    return jsonify(group), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
