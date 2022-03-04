"""
TODO: Module Docstring
"""
import os
import sys

from pymongo import MongoClient

if len(sys.argv) != 3:
    print('Usage: python3 setup_db.py [admin-username] [admin-password]')
    sys.exit()

print(f"Admin Username: {sys.argv[1]}")
# print(sys.argv[2])

# create the connection
print("Attempting to connect to MongoDB...")
client = MongoClient(host=os.environ['MONGO_HOST'],
                     username=sys.argv[1],
                     password=sys.argv[2],
                     authSource='admin')

db = client['smart-ledger']

# check if the mongodb user is already created
listing = db.command('usersInfo')
for document in listing['users']:
    if document['user'] == os.environ['API_USERNAME']:
        print("The API user already exists...")
        sys.exit()

# create the user
db.command('createUser',
           os.environ['API_USERNAME'],
           pwd=os.environ['API_PASSWORD'],
           roles=['readWrite'])

print("Successfully created API user!")
