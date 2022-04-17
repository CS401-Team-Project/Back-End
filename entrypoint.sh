#!/bin/bash

echo "#################################################################"
echo "## START                 entrypoint.sh                         ##"
echo "#################################################################"

INTERPRETER=python3
if ! command -v "$INTERPRETER" &> /dev/null
then
    INTERPRETER=python
    if ! command -v "$INTERPRETER" &> /dev/null
    then
      echo "ERROR: $INTERPRETER could not be found"
      exit
    fi
fi
echo "# Using: $INTERPRETER"
echo "# DEBUG: $DEBUG"

# TODO: Change default admin credentials for MongoDB or lock admin account
ADMIN_USER=admin
ADMIN_PASS=password

echo "## Printing Environment Variables...                           ##"
# TODO: don't log sensitive information when DEBUG=False

env

echo "#################################################################"
echo "## 1. Installing Python Requirements...                           ##"
$INTERPRETER -m pip install -r requirements.txt
echo "#################################################################"

echo "## 2. Creating MongoDB API user..."
$INTERPRETER ./scripts/CreateApiUser.py $ADMIN_USER $ADMIN_PASS || exit 1;

# TODO: Adding test data to MongoDB if DEBUG env variable is set

echo "## 4. Starting API Server with Gunicorn"
gunicorn --bind 0.0.0.0:5000 App:app

echo "#################################################################"
echo "## END                   entrypoint.sh                         ##"
echo "#################################################################"