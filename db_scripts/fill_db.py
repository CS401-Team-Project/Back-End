import json
import os
import numpy as np
from flask import Flask
from flask_mongoengine import MongoEngine


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': os.environ['MONGODB_HOST'],
    'username': os.environ['MONGODB_USERNAME'],
    'password': os.environ['MONGODB_PASSWORD'],
    'authSource': 'smart-ledger',
    'db': 'smart-ledger',

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

# add people to database
with open('db_scripts/example_data/people.json', 'r') as f:
    people_data = json.load(f)

for person in people_data:
    Person(**person).save()

# add groups to database
with open('db_scripts/example_data/groups.json', 'r') as f:
    group_data = json.load(f)

for group in group_data:
    Group(**group).save()

# randomly link people to groups
people = Person.objects()
groups = Group.objects()


num_groups = len(people)
num_people = len(groups)

for g in groups:
    people_to_add = np.unique(np.random.randint(0, num_people, np.random.randint(3, num_people+1)))
    for i, p in enumerate(people):
        if i in people_to_add:
            p.groups.append(g.id)
            p.save()
            g.people.append(p.id)
            g.save()

