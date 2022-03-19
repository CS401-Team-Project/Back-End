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


def verify_token():
    """
    verify the given token
    :return: return a dictionary of the persons info from google
    """
    token = request.args.get('token')
    try:
        # verify the token
        token_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        # check validity of toke issuer
        if token_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # recheck client id
        if token_info['aud'] != CLIENT_ID:
            raise ValueError('Client ID does not match.')

        person = {
            'first_name': token_info['given_name'],
            'last_name': token_info['family_name'],
            'email': token_info['email'],
            'token': token_info['sub'],
            'token_exp': datetime.datetime.fromtimestamp(token_info['exp'])
        }
        return person, 200
    except ValueError as e:
        # Invalid token
        return {"error": str(e)}, 404


# TODO
def update_token(person):
    """
    check token exp date and update it if needed
    :param person: a person object from the database
    :return:
    """
    pass


@app.route('/register', methods=['GET'])
def register():
    token = verify_token()
    if token[1] == 404:
        return jsonify(token[0]), token[1]

    person_dict = token[0]
    person = Person.objects(email=person_dict['email']).first()

    # TODO - verify that None is returned if the persons email is not found
    # if person not in DB create them
    if person is None:
        person = Person(first_name=person_dict['first_name'],
                       last_name=person_dict['last_name'],
                       email=person_dict['email'],
                       token=person_dict['token'],
                       token_exp=person_dict['token_exp'])
        person.save()

    # return OK message
    return jsonify({'msg': 'OK'}), 200


@app.route('/get_group', methods=['GET'])
def get_group():
    token = verify_token()
    if token[1] == 404:
        return jsonify(token[0]), token[1]

    # check if person is in db
    person = Person.objects(email=token[0]['email']).first()
    if person is None:
        return jsonify({'error': 'Person not found'})

    # check token date
    update_token(person)

    # list of groups [{id: name}...]
    group_list = []

    # go through list of group ids that person is in and get group names
    g_ids = person['groups']
    for g_id in g_ids:
        group = Group(id=g_id)
        group_list.append({'g_id': group['name']})

    # return list of groups
    return jsonify({'groups': group_list}), 200


if __name__ == "__main__":
    # TODO: Change to production debug False
    app.run(debug=True, port=5000)
