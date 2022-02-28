#!/bin/bash

echo "#################################################################"
echo "## START                 entrypoint.sh                         ##"
echo "#################################################################"

# TODO: Change default admin credentials for MongoDB or lock admin account
ADMIN_USER=admin
ADMIN_PASS=password

echo "## Creating MongoDB API user..."
python ./scripts/create_api_user.py $ADMIN_USER $ADMIN_PASS || exit 1;

echo "## Filling Database with test data..."
python ./scripts/fill_db.py $ADMIN_USER $ADMIN_PASS || exit 1;

echo "## Starting API Server with Gunicorn"
gunicorn --bind 0.0.0.0:5000 app:app

echo "#################################################################"
echo "## END                   entrypoint.sh                         ##"
echo "#################################################################"