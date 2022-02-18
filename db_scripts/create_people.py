import json
import os
from flask import Flask
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

with open('db_scripts/example_data/people.json', 'r') as f:
    people_data = json.load(f)

for person in people_data:
    Person(**person).save()