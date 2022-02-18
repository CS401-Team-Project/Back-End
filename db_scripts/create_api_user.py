import os
import sys
from pymongo import MongoClient

if len(sys.argv) != 3:
    print('python3 setup_db.py [username] [password]')
    sys.exit()

# create the connection
client = MongoClient(host=os.environ['MONGODB_HOST'],
                     username=sys.argv[1],
                     password=sys.argv[2],
                     authSource='admin')
db = client['smart_ledger']

# check if the mongodb user is already created
listing = db.command('usersInfo')
for document in listing['users']:
    if document['user'] == os.environ['MONGODB_USERNAME']:
        sys.exit()

# create the user
db.command('createUser', os.environ['MONGODB_USERNAME'], pwd=os.environ['MONGODB_PASSWORD'], roles=['readWrite'])

