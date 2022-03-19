"""
Main api request endpoint
"""
import os
import datetime

from google.oauth2 import id_token
from google.auth.transport import requests

from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

from Models import Person, Group

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
    """

    :return:
    """
    print(f"ROUTE get_person(): {request}")
    email = request.args.get('email')
    person = Person.objects(email=email).first()
    return jsonify(person), 200


@app.route("/group", methods=['GET'])
def get_group():
    """

    :return:
    """
    print(f"ROUTE get_group: {request}")
    g_id = request.args.get('id')
    group = Group.objects(id=g_id).first()
    return jsonify(group), 200

@app.route("/test", methods=['GET'])
def test():
    """
    Just a test route to verify that the API is working.
    :return: Smart Ledger API Endpoint: OK
    """
    print(f"ROUTE test: {request}")
    return "Smart Ledger API Endpoint: OK", 200

# dont hardcode this. Will fix at later date
CLIENT_ID = '996982688294-rqhcr4d5b6m3vk0e3ur2no457iqql2u5.apps.googleusercontent.com'

@app.route("/register")
def check_if_registered():
    token = request.form["idtoken"]
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        num_results = Person.objects(sub=userid).count()

        # User in database if 1. Not in database if 0
        return num_results

    except ValueError:
        # Invalid token
        return -1


@app.route("/register")
def register_user():
    token = request.form["idtoken"]
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        f_name = idinfo['given_name']
        l_name = idinfo['family_name']
        em = idinfo['email']
        exp = datetime.datetime.fromtimestamp(idinfo['exp'])
        p = Person(first_name=f_name, last_name=l_name, email=em, sub=userid, token_latest=token, token_exp=exp).save()
        return 1

    except ValueError:
        # Invalid token
        return -1


if __name__ == "__main__":
    # TODO: Change to production debug False
    app.run(debug=True, port=5000)
