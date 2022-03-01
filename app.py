"""
TODO: Module Docstring
"""
import os

from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

from models import Person, Group

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': os.environ['MONGO_HOST'],
    'username': os.environ['API_USERNAME'],
    'password': os.environ['API_PASSWORD'],
    'authSource': 'smart-ledger',
    'db': 'smart-ledger'
}

db = MongoEngine()
db.init_app(app)


@app.route("/person", methods=['GET'])
def get_person():
    print(f"ROUTE get_person(): {request}")
    email = request.args.get('email')
    person = Person.objects(email=email).first()
    return jsonify(person), 200


@app.route("/group", methods=['GET'])
def get_group():
    print(f"ROUTE get_group: {request}")
    g_id = request.args.get('id')
    group = Group.objects(id=g_id).first()
    return jsonify(group), 200


if __name__ == "__main__":
    # TODO: Change to production debug False
    app.run(debug=True, port=5000)
