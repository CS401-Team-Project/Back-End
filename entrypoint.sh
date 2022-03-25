#!/bin/bash

echo "#################################################################"
echo "## START                 entrypoint.sh                         ##"
echo "#################################################################"

# TODO: Figure out what needs to be done with the API user and password storing
#export MONGO_HOST="mongodb"
#export API_USERNAME="apiuser"
#export API_PASSWORD="apipassword"
#export CLIENT_ID="996982688294-rqhcr4d5b6m3vk0e3ur2no457iqql2u5.apps.googleusercontent.com"
# TODO: Change default admin credentials for MongoDB or lock admin account
ADMIN_USER=admin
ADMIN_PASS=password

echo "## Printing Environment Variables...                           ##"
# TODO: don't log sensitive information
env

echo "#################################################################"
echo "## 1. Installing Python Requirements...                           ##"
python -m pip install -r requirements.txt
echo "#################################################################"

echo "## 2. Creating MongoDB API user..."
python ./scripts/CreateApiUser.py $ADMIN_USER $ADMIN_PASS || exit 1;

# TODO: Adding test data to MongoDB if DEBUG env variable is set
#echo "## 3. Filling Database with test data..."
#python ./scripts/FillDB.py || exit 1;

echo "## 4. Starting API Server with Gunicorn"
gunicorn --bind 0.0.0.0:5000 App:app

echo "#################################################################"
echo "## END                   entrypoint.sh                         ##"
echo "#################################################################"