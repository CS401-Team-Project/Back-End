"""
Main api request endpoint
"""
import os
from functools import wraps
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


@app.route("/test", methods=['GET'])
def test():
    """
    Just a test route to verify that the API is working.
    :return: Smart Ledger API Endpoint: OK
    """
    print(f"ROUTE test: {request}")
    return "Smart Ledger API Endpoint: OK", 200


def verify_token(func):
    """
    verify the given token
    :return: return a dictionary of the persons info from google
    """

    @wraps(func)
    def wrap(*args, **kwargs):
        """
        wrap the given function
        """
        try:
            # get token
            token = request.args.get('token')

            # verify the token
            token_info = id_token.verify_oauth2_token(token, requests.Request(), os.environ['CLIENT_ID'])

            # verify the subject
            sub = token_info['sub']

            # get the person
            person = Person.objects.get(sub=sub)

            # call the wrapped function
            return func(person, *args, **kwargs)

        except Exception as exp:
            # Invalid token
            return jsonify({"msg": str(exp)}), 401

    return wrap


@app.route('/register', methods=['GET'])
def register():
    """
    used for logging in a user. creates an account if not already exists
    """
    # get token
    token = request.args.get('token')
    print(token)
    # verify the token
    token_info = id_token.verify_oauth2_token(token, requests.Request(), os.environ['CLIENT_ID'])
    print(token_info)

    # verify the subject
    sub = token_info['sub']
    print(sub)
    person = Person.objects(sub=sub)

    if len(person) > 1:
        return jsonify({'msg', 'Too many people returned.'}), 401
    person = person.first()
    print(type(person))
    print(person)
    # if person not in DB create them
    if person is None:
        print("person no exist creating them")
        # TODO - add email verified and handle it
        person = Person(first_name=token_info['given_name'],
                        last_name=token_info['family_name'],
                        email=token_info['email'],
                        sub=token_info['sub'],
                        picture=token_info['picture'])
        person.save()
    print(person)

    # return OK message
    return jsonify({'msg': 'OK'}), 200


@app.route('/user_profile', methods=['GET'])
@verify_token
def user_profile(person):
    """
    get the currently logged in person
    """
    if 'sub' in request.args:
        try:
            # requesting another users info
            person = Person.objects.get(sub=request.args.get('sub'))

            # explicitly build the returned json
            ret = {
                'email': person['email'],
                'first_name': person['first_name'],
                'last_name': person['last_name'],
                'picture': person['picture'],
                'sub': person['sub'],
                'date_joined': person['date_joined']
            }
            return jsonify(ret), 200

        except Exception as exp:
            return jsonify({'msg': exp}), 500
    # else return the users info
    return jsonify(person), 200

@app.route('/get_groups', methods=['GET'])
@verify_token
def get_groups(person):
    """
    get the groups the user belongs to
    """
    try:
        # list of groups [{id: name}...]
        group_list = []

        # go through list of group ids that person is in and get group names
        g_ids = person['groups']
        for g_id in g_ids:
                group = Group.objects.get(id=g_id)
                group_list.append({g_id: group['name']})
        # return list of groups
        return jsonify({'groups': group_list}), 200
    except Exception as exp:
        return jsonify({'msg': exp}), 505

if __name__ == "__main__":
    # TODO: Change to production debug False
    app.run(debug=True, port=5000)
