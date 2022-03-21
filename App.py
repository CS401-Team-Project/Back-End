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

# setup the Flask server
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
            # get the request args depending on the type of request
            request_data = {}
            if request.method == "POST":
                request_data = request.get_json(force=True, silent=True)
            elif request.method == "GET":
                request_data = request.args

            # get the token from the request
            token = request_data.get('token')

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


###############################################################################################################
## PERSON API ENDPOINTS


@app.route('/register', methods=['POST'])
def register():
    """
    used for logging in a user. creates an account if not already exists
    :return: status of the registration
    """
    try:
        print('request\n', request)
        request_data = request.get_json(force=True, silent=True)

        if request_data is None:
            raise Exception('Request could not be parsed.')

        # get token
        token = request_data.get('token')
        print('token', token)

        # verify the token
        token_info = id_token.verify_oauth2_token(token, requests.Request(), os.environ['CLIENT_ID'])
        print('token_info', token_info)

        # get the subject
        sub = token_info['sub']

        # attempt to get the person
        # NOTE - this needs to not be an objects.get call because that will throw error when there is no user
        person = Person.objects(sub=sub)
        print('person', person)

        # if there are more than one people returned. thats a problem
        if len(person) > 1:
            return jsonify({'msg': 'Too many people returned.'}), 401

        # get the person that is returned
        person = person.first()

        # if person not in DB create them
        msg = 'User Exists'
        if person is None:
            # TODO - add email verified and handle it

            # create the person object
            person = Person(first_name=token_info['given_name'],
                            last_name=token_info['family_name'],
                            email=token_info['email'],
                            sub=token_info['sub'],
                            picture=token_info['picture'])

            # save the person object
            person.save()
            msg = 'User Created'

        # return status message
        return jsonify({'msg': msg}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/user_profile', methods=['POST'])
@verify_token
def user_profile(person):
    """
    get a persons profile information.
    If the sub param is NOT passed, will return the current users profile info
    If the sub param is passed, will return the given sub profile info

    :param person: current logged in user
    :return: returns json of
    """
    try:
        request_data = request.get_json(force=True, silent=True)

        # if sub was given to us
        if 'sub' in request_data:
            # requesting another users info
            person = Person.objects.get(sub=request_data.get('sub'))

            # explicitly build the returned json
            ret = {
                'first_name': person['first_name'],
                'last_name': person['last_name'],
                'picture': person['picture'],
                'sub': person['sub'],
                'date_joined': person['date_joined']
            }
            return jsonify(ret), 200

        # else return the users info
        return jsonify(person), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/get_groups', methods=['POST'])
@verify_token
def get_groups(person):
    """
    get the groups the user belongs to
    token needs to be passed in the request
    :param person: current logged in user
    :return:
    """

    try:
        # list of groups [{id: name}...]
        group_list = []

        # go through list of group ids that person is in and get group names
        g_ids = person['groups']
        for g_id in g_ids:
            # retrieve the groups name
            group = Group.objects.get(id=g_id)
            group_list.append({g_id: group['name']})
        # return list of groups
        return jsonify(group_list), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


###############################################################################################################
## GROUP API ENDPOINTS

@app.route('/get_members', methods=['POST'])
@verify_token
def get_members(_):
    """
    Get a list of members that belong to a group
    request must contain a token and a group id
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        g_id = request_data.get('id')

        # query the group
        group = Group.objects.get(id=g_id)

        # get the members
        members = group.people

        return jsonify(members), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/create_group', methods=['POST'])
@verify_token
def create_group(person):
    """
    Create a group add the creator to the group
    request must contain:
        - token
        - name: group name
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_name = request_data.get('name')

        # create the group
        group = Group(name=group_name)

        # add the creating user to the group
        group.people.append(person.sub)

        # save the group
        group.save()

        # add the groups id to the persons list of groups
        person.groups.append(group.id)

        # save the person object
        person.save()

        return jsonify({'id': group.id, 'msg': 'Created group'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500

if __name__ == "__main__":
    app.run(debug=bool(os.environ['DEBUG']), port=5000)
