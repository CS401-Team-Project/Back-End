import datetime
import os

from flask import Flask, Response, request, jsonify
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': os.environ['MONGODB_HOST'],
    'username': os.environ['MONGODB_USERNAME'],
    'password': os.environ['MONGODB_PASSWORD'],
    'db': 'smart-ledger'
}

db = MongoEngine()
db.init_app(app)

class Person(db.Document):
    first_name = db.StringField(max_length=60, required=True)
    last_name = db.StringField(max_length=60, required=True)
    email = db.StringField(max_length=60, required=True)

@app.route("/Person/", methods=['POST'])
def add_person():
    body = request.get_json()
    print(body)
    person = Person(**body).save()
    return jsonify(person), 201

@app.route("/Person/", methods=['GET'])
def get_people():
    person = Person.objects()
    return jsonify(person), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
