"""
Main api request endpoint
"""

import os
import array
import base64
import tempfile
import datetime
import traceback
from copy import deepcopy
from functools import wraps
import flask_limiter.errors
from bson.objectid import ObjectId
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from Models import Person, Group, Item, TransactionItem, Transaction, Receipt
from mongoengine import *

# setup the Flask server
app = Flask(__name__)
limiter = Limiter(app,
                  key_func=get_remote_address,
                  default_limits=['20/second'])

debug = os.environ.get('DEBUG', False)
debug = bool(debug)

print(f"# DEBUG: {debug}")

# If on debug allow cross-origin resource sharing
if debug:
    CORS(app)

mongo_host = os.environ.get('MONGO_HOST', 'localhost')
mongo_port = os.environ.get('MONGO_PORT', 27017)
mongo_username = os.environ.get('API_USERNAME', None)
mongo_password = os.environ.get('API_PASSWORD', None)

# If Mongo Username is None, print warning
if mongo_username is None:
    print("WARNING: MongoDB username is None!!")

# If Mongo Password is None, print warning
if mongo_password is None:
    print("WARNING: MongoDB password is None!!")

app.config['MONGODB_SETTINGS'] = {
    'host': mongo_host,
    'username': mongo_username,
    'password': mongo_password,
    'authSource': 'smart-ledger',
    'db': 'smart-ledger'
}

db = MongoEngine()
db.init_app(app)


def print_info(func):
    """
    verify the given token
    :return: return a dictionary of the persons info from google
    """

    @wraps(func)
    def wrap(*args, **kwargs):
        """
        wrap the given function
        """
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        path = request.path

        print(f"{ip} : {path} : {request} @ {datetime.datetime.now()}")
        try:
            ret = func(*args, **kwargs)
            print(f"    |--> {ret[0].get_json()['msg']} : {ret[1]}")
            return ret
        except flask_limiter.errors.RateLimitExceeded as exp:
            print(f"{ip} : {path} => Exception: {exp} @ {datetime.datetime.now()}")
            traceback.print_exc()
            print(f"    |--> Rate limit exceeded. : 429")
            return jsonify({'msg': 'Rate limit exceeded.'}), 429
        except Exception as exp:
            print(f"{ip} : {path} => Exception: {exp} @ {datetime.datetime.now()}")
            traceback.print_exc()
            print(f"    |--> An unexpected error occurred. : 500")
            return jsonify({'msg': 'An unexpected error occurred.'}), 500

    return wrap


###############################################################################################################
###############################################################################################################
###############################################################################################################
# TEST API ENDPOINTS

@app.route("/test_get", methods=['GET'])
@print_info
@limiter.limit("10/second", override_defaults=False)
def test_get():
    """
    Just a test route to verify that the API is working.
    :return: Smart Ledger API Endpoint: OK
    """
    return jsonify({'msg': "Smart Ledger API Endpoint: OK"}), 200


@app.route("/test_post", methods=['POST'])
@print_info
def test_post():
    """
    Just a test route to verify that the API is working.
    :return: Smart Ledger API Endpoint: OK
    """
    request_data = request.get_json(force=True)

    try:
        n1 = float(request_data.get('n1'))
        n2 = float(request_data.get('n2'))
        op = request_data.get('op')
    except ValueError:
        return jsonify({'msg': "Invalid data"}), 400

    if op == "add":
        return jsonify({'ans': str(n1 + n2), 'msg': 'Calculated Answer'}), 200
    elif op == "sub":
        return jsonify({'ans': str(n1 - n2), 'msg': 'Calculated Answer'}), 200
    elif op == "mul":
        return jsonify({'ans': str(n1 * n2), 'msg': 'Calculated Answer'}), 200
    elif op == "div":
        return jsonify({'ans': str(n1 / n2), 'msg': 'Calculated Answer'}), 200
    else:
        return jsonify({'msg': "Unsupported operation"}), 501


###############################################################################################################
###############################################################################################################
###############################################################################################################
# WRAPPERS

def get_token(req):
    # if behind a proxy
    headers = req.headers
    # Get the authorization header
    bearer = headers.get('Authorization')  # Bearer YourTokenHere
    # Get the token from the authorization header
    token = bearer.split()[1]  # YourTokenHere
    return token


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
            # Get the token from the authorization header
            token = get_token(request)

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
            print(f"verify_token() => Exception: {exp} @ {datetime.datetime.now()}")
            return jsonify({'msg': 'Token is unauthorized or user does not exist.'}), 404

    return wrap


###############################################################################################################
###############################################################################################################
###############################################################################################################
## PERSON API ENDPOINTS


@app.route('/register', methods=['POST'])
@print_info
def register():
    """
    used for logging in a user. creates an account if not already exists
    :return: status of the registration
    """
    token = get_token(request)
    # verify the token
    token_info = id_token.verify_oauth2_token(
        token,
        requests.Request(),
        os.environ['CLIENT_ID'],
        clock_skew_in_seconds=5
    )

    # get the subject
    sub = token_info['sub']

    # attempt to get the person
    # NOTE - this needs to not be an objects.get call because that will throw error when there is no user
    person = Person.objects(sub=sub)

    # if there are more than one people returned. thats a problem
    if len(person) > 1:
        return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400

    # get the person that is returned
    person = person.first()

    # if person not in DB create them
    if person is None:
        # create the person object
        person = Person(first_name=token_info['given_name'],
                        last_name=token_info['family_name'],
                        email=token_info['email'],
                        sub=token_info['sub'],
                        picture=token_info['picture'])

        status_code = 201
    else:
        status_code = 200

    # save the person object
    person.date.last_login = datetime.datetime.now(datetime.timezone.utc)
    person.save()

    # return status message
    return jsonify({'msg': 'User successfully retrieved.', 'data': person}), status_code


@app.route('/user/info', methods=['POST'])
@verify_token
@print_info
def user_profile(person):
    """
    get a persons profile information.
    If the sub param is NOT passed, will return the current users profile info
    If the sub param is passed, will return the given sub profile info

    :param person: current logged in user
    :return: returns json of
    """
    request_data = request.get_json(force=True)

    # if sub was given to us
    if 'sub' in request_data and request_data.get('sub') != person.sub:
        person = Person.objects(sub=request_data.get('sub'))
        if len(person) == 0:
            return jsonify({'msg': 'Token is unauthorized or user does not exist.'}), 404
        person = person.first()

        # explicitly build the returned json
        date = {
            'created': person['date']['created']
        }
        person = {
            'sub': person['sub'],
            'first_name': person['first_name'],
            'last_name': person['last_name'],
            'email': person['email'],
            'email_verified': person['email_verified'],
            'picture': person['picture'],
            'date': date,
            'pay_with': person['pay_with']
        }

    # return the users info
    return jsonify({'msg': 'User successfully retrieved.', 'data': person}), 200


@app.route('/user/update', methods=['POST'])
@verify_token
@print_info
def update_profile(person):
    """
    modify a users profile
    :return: returns json of
    """
    # get fields
    request_data = request.get_json(force=True, silent=True)
    profile = request_data['data']

    # check for unallowed fields
    if set(profile.keys()).intersection({'email', 'sub', 'date_joined', 'picture', 'groups'}):
        return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400

    # iterate through given fields
    for k, v in profile.items():
        if k not in person:
            return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400

        # if key is pay_with must iterate through embedded dictionary
        elif k == 'pay_with':
            for k2, v2 in v.items():
                person[k][k2] = v2
        # set the keyed value
        else:
            person[k] = v

    # save the person
    person.date.updated = datetime.datetime.now(datetime.timezone.utc)
    person.save()
    return jsonify({'msg': 'Successfully updated the user profile.'}), 200


@app.route('/user/delete', methods=['POST'])
@verify_token
@print_info
def delete_profile(person):
    """
    delete a users profile
    :param person: current logged in user
    :return: returns json of
    """

    # TODO - we need to figure out a policy to show users past transactions after their account has been deleted

    # unlink person from all groups
    for g_id in person.groups:
        group = Group.objects(id=g_id)
        if len(group) == 0:
            continue
        group = group.first()
        if person.sub in group.members:
            group.members.remove(person.sub)


    # delete the person from the database
    person.delete()
    return jsonify({'msg': 'Successfully deleted the user profile.'}), 200


###############################################################################################################
###############################################################################################################
###############################################################################################################
## GROUP API ENDPOINTS

###############################################################################################################
## GROUP CREATION/DELETION

@app.route('/group/create', methods=['POST'])
@verify_token
@print_info
def create_group(person):
    """
    Create a group add the creator to the group
    request must contain:
        - token
        - data
            - name: group name
            - desc: [optional]
            - invites: [optional] array of emails
    :param person: the person making the request
    :return: returns json with group id and msg
    """

    # get the request data
    request_data = request.get_json(force=True, silent=True)
    data = request_data.get('data')
    if 'name' not in data:
        return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400

    group_name = data['name']
    group_desc = data.get('desc')
    invite = data.get('invites')

    # create the group
    group = Group(name=group_name, desc=group_desc, admin=person.sub)

    # add the creating user to the group
    group.members.append(person.sub)

    # add admin to the balances dict
    group.restricted.balances[person.sub] = {}

    # add admin to ledger
    group.restricted.ledger[person.sub] = 0

    # save the group
    group.save()

    # add the groups id to the persons list of groups
    person.groups.append(group.id)

    # save the person object
    person.date.updated = datetime.datetime.now(datetime.timezone.utc)
    person.save()

    if invite is not None:
        if not isinstance(invite, list):
            return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400
        for email in invite:
            group.restricted.invite_list.append(email)

            # save the invite in the person
            p = Person.objects(email=email)
            if len(p) == 0:
                continue
            p = p.first()
            if group.id not in p.invites:
                p.invites.append(group.id)
            p.date.updated = datetime.datetime.now(datetime.timezone.utc)
            p.save()

    # save the group
    group.save()
    return jsonify({'msg': 'Group successfully created.', 'data': group}), 200


@app.route('/group/delete', methods=['POST'])
@verify_token
@print_info
def delete_group(person):
    """
    Create a group add the creator to the group
    request must contain:
        - token
        - id: group id
    :param person: the person making the request
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    group_id = request_data['id']

    # query the group
    group = Group.objects(id=group_id)
    if len(group) == 0 or person.sub != group.first().admin:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404

    group = group.first()

    # Iterate through people and unlink them from the groups
    for p_sub in group.members:

        # try to get the person from the DB
        person = Person.objects(sub=p_sub)
        if len(person) == 0:
            continue
        person = person.first()

        # try to remove person from group
        person.groups.remove(ObjectId(group_id))
        person.date.updated = datetime.datetime.now(datetime.timezone.utc)
        person.save()

    # iterate through transactions and items to decrement the item counts. waiting on items to be implemented
    for t_id in group.restricted.transactions:
        # try to get the transaction
        transaction = Transaction.objects(id=t_id)
        if len(transaction) == 0:
            continue
        transaction = transaction.first()
        _delete_transaction(group, transaction)

    return jsonify({'msg': 'Group successfully deleted.'}), 200


@app.route('/group/info', methods=['POST'])
@verify_token
@print_info
def get_group(person):
    """
    Return a group the user is in
    request must contain:
        - token
        - id: group id
    :param person: the person making the request
    :return: returns json with group id and msg
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    group_id = request_data.get('id')

    if group_id is None:
        return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400

    # get the group
    group = Group.objects.get(id=group_id)

    # check if user is in group
    if person.sub not in group.members:
        group.restricted = None

    # return the group
    return jsonify({'msg': 'Group successfully retrieved.', 'data': group}), 200


@app.route('/group/update', methods=['POST'])
@verify_token
@print_info
def update_group(person):
    """
    Return a group the user is in
    request must contain:
        - token
        - id: group id
        - group: dictionary that holds all fields you want to change
    :param person: the person making the request
    :return: returns json with group id and msg
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    group_id = request_data.get('id')
    data = request_data.get('data')

    # get the group
    group = Group.objects(id=group_id)
    if len(group) == 0:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404
    group = group.first()

    # check if user is in group
    if person.sub not in group.members:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404

    # weed out bad fields
    if not set(data.keys()).intersection({'name', 'description', 'restricted'}):
        return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400

    # iterate through all items
    for k, v in data.items():
        # if is join code check if authorized
        if k == 'restricted':
            for k2, v2 in v.items():
                if k2 == 'permissions':
                    if person.sub != group.admin:
                        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404
                    for k3, v3 in v2.items():
                        group[k][k3] = v3
        else:
            group[k] = v

    group.restricted.date.update = datetime.datetime.now(datetime.timezone.utc)

    # save the group
    group.save()

    # return the group
    return jsonify({'msg': 'Group successfully updated.'}), 200


###############################################################################################################
## GROUP MEMBER ADD/REMOVE


@app.route('/group/join', methods=['POST'])
@verify_token
@print_info
def join_group(person):
    """
    Add a member to the group
    request must contain:
        - token
        - id: group id
    :param person: the person making the request
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    group_id = request_data.get('id')

    # query the group
    group = Group.objects(id=group_id)

    if len(group) == 0:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404
    group = group.first()

    # check if already a member
    if person.sub in group.members:
        return jsonify({'msg': 'User is already a member of the group.'}), 409

    if person.email in group.restricted.invite_list:
        group.restricted.invite_list.remove(person.email)

    # add person to group
    group.members.append(person.sub)
    group.updated = datetime.datetime.now(datetime.timezone.utc)

    # add person to the balances dict
    group.restricted.balances[person.sub] = {}
    for p in group.members:
        if p != person.sub:
            group.restricted.balances[person.sub][p] = 0
            group.restricted.balances[p][person.sub] = 0

    # add person to ledger
    group.restricted.ledger[person.sub] = 0

    # save group
    group.save()

    # link group to member
    person.groups.append(group.id)

    # save person
    person.date.updated = datetime.datetime.now(datetime.timezone.utc)
    person.save()

    return jsonify({'msg': 'User joined group.'}), 200


@app.route('/group/invite', methods=['POST'])
@verify_token
@print_info
def invite_group(person):
    """
    invite a member to the group
    request must contain:
        - token
        - id: group id
        - emails: [list] person to be invited
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    group_id = request_data.get('id')
    emails = request_data.get('emails')

    # query the group
    group = Group.objects(id=group_id)
    if len(group) == 0:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404
    group = group.first()

    # if the user is not an admin then cannot invite
    if group.restricted.permissions.only_admin_invite and person.sub != group.admin:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404

    for email in emails:
        # check if already invited
        if email in group.restricted.invite_list:
            return jsonify({'msg': 'User is already a invited.'}), 409

        # check if already in the group
        for sub in group.members:
            p = Person.objects.get(sub=sub)
            if p.email == email:
                continue

        # add person to group invite list
        group.restricted.invite_list.append(email)

        # if person exists in the db add this to their invites
        p = Person.objects(email=email)
        if len(p) != 0:
            p = p.first()
            if group.id not in p.invites:
                p.invites.append(group.id)
                p.save()

    # save group
    group.restricted.date.updated = datetime.datetime.now(datetime.timezone.utc)
    group.save()
    return jsonify({'msg': 'Invitation(s) successfully created.'}), 200


@app.route('/group/remove-member', methods=['POST'])
@verify_token
@print_info
def remove_member(person):
    """
    Add a member to the group
    request must contain:
        - token
        - id: group id
        - userid: [optional] user to remove from the grou
    :param person: the person making the request
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    group_id = request_data.get('id')
    sub = request_data.get('userid')

    # query the group
    group = Group.objects(id=group_id)
    if len(group) == 0:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404
    group = group.first()

    # if the user is trying to delete another user in the group
    if sub is None:
        # if person is trying to delete themselves from the group
        sub = person.sub

    elif (group.settings.only_admin_remove_user and group.admin != person.sub) or sub == group.admin:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404

    # check if the given sub is not in group
    if sub not in group.members:
        return jsonify({'msg': 'User is not a member of the group.'}), 409

    # remove the person from the group
    group.members.remove(sub)

    # save the group
    group.updated = datetime.datetime.now(datetime.timezone.utc)
    group.save()

    # if group is tied to person object
    if group_id in person.groups:
        # remove group from person
        person.groups.remove(group_id)

        # save person
        person.date.updated = datetime.datetime.now(datetime.timezone.utc)
        person.save()

    return jsonify({'msg': 'Member successfully removed.'}), 200


@app.route('/group/refresh-id', methods=['POST'])
@verify_token
@print_info
def refresh_id(person):
    """
    refreshes the group id
    request must contain:
        - token
        - id: group id
    :param person: the person making the request
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    group_id = request_data.get('id')

    # query the group
    group = Group.objects(id=group_id)
    if len(group) == 0:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404
    group = group.first()

    # is person admin
    if person.sub != group.admin:
        return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404

    old_group = group
    group = deepcopy(old_group)
    group.id = None

    # TODO: need to update all links in person and Transaction DB

    # update times
    time = datetime.datetime.now(datetime.timezone.utc)
    group.updated = time
    group.last_refreshed = time

    # save the group
    group.save()
    old_group.delete()
    return jsonify({'msg': "Group's unique identifier successfully refreshed.", 'id': group.id}), 200


###############################################################################################################
###############################################################################################################
###############################################################################################################
## TRANSACTIONS


@app.route('/transaction/create', methods=['POST'])
@verify_token
@print_info
def create_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - id: group id
        - title: transaction title required
        - desc: optional
        - vendor: optional
        - date: optional
        - who_paid: [dictionary] contains key value pairs of who paid and how much
        - items: array containing jsons of items to add to the transaction
            - item: can have optional total price
    :param person: the person making the request
    :return: returns a transaction id used to link items to the transaction
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    group_id = request_data.get('id')
    title = request_data.get('title')
    desc = request_data.get('desc')
    vendor = request_data.get('vendor')
    who_paid = request_data.get('who_paid')
    date = request_data.get('date')
    items = request_data.get('items')

    if group_id is None or title is None or items is None:
        return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

    if date is None:
        date = datetime.datetime.now(datetime.timezone.utc)

    # query the group to make sure it exists
    group = Group.objects.get(id=group_id)

    # make sure the user belongs to the group
    if person.sub not in group.members:
        return jsonify({'msg': 'Token is unauthorized.'}), 404

    # can't calculate who_paid later on
    if items is None and who_paid is None:
        return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

    # create the transaction
    transaction = Transaction(title=title,
                              group=group_id,
                              desc=desc,
                              vendor=vendor,
                              created_by=person.sub,
                              modified_by=person.sub,
                              date_purchased=date,
                              who_paid=who_paid)

    # save the transaction
    transaction.save()

    # init transaction deltas
    balance_deltas = {}
    for p1 in group.members:
        balance_deltas[p1] = {}
        for p2 in group.members:
            if p1 != p2:
                balance_deltas[p1][p2] = 0
    transaction.balance_deltas = balance_deltas
    transaction.save()

    # init the ledger deltas
    for p in group.members:
        if p in who_paid:
            transaction.ledger_deltas[p] = who_paid[p]
        else:
            transaction.ledger_deltas[p] = 0
    transaction.save()

    # add all give items
    total_used = 0
    if items is not None:
        for item in items:
            person_id = item.get('owed_by')

            # get the item data from the request
            name = item.get('name')
            desc = item.get('desc')

            total_price = item.get('total_price')
            quantity = item.get('quantity')
            unit_price = item.get('unit_price')

            if total_price is None and (quantity is None or unit_price is None):
                transaction.delete()
                return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

            if (quantity is None and unit_price is None) and total_price is None:
                transaction.delete()
                return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

            if name is None:
                return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

            if total_price is not None and (quantity is None or unit_price is None):
                quantity = 1
                unit_price = total_price

            # keep track of the total_used
            total_used += (quantity * unit_price)

            # add the item to the transaction
            _add_item_to_transaction(person, transaction, quantity, person_id, name, desc, unit_price)
            transaction.reload()

    # update the who paid
    total_paid = 0
    if who_paid is None:
        total_paid = total_used
        transaction.who_paid[person.sub] = total_used
    else:
        for k, v in who_paid.items():
            total_paid += v
            transaction.who_paid[person.sub] = v

    if total_paid != total_used:
        _delete_transaction(group, transaction)
        return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

    # # update the ledger
    # for k, v in transaction.ledger_deltas.items():
    #     group.restricted.ledger[k] += v

    # update group with the ledger deltas
    for k, v in transaction.ledger_deltas.items():
        group.restricted.ledger[k] += v

    # update group with the balance deltas
    for p1, d in transaction.balance_deltas.items():
        for p2, v in d.items():
            group.restricted.balances[p1][p2] += v
    # update the balance deltas
    print('=' * 30)
    print(transaction.ledger_deltas)
    print(transaction.balance_deltas)
    print('-' * 30)
    print(group.restricted.ledger)
    print(group.restricted.balances)
    print('=' * 30)

    # save the transaction
    transaction.save()

    # append the transaction to the group
    group.restricted.transactions.append(transaction.id)

    # save the group
    group.save()
    return jsonify({'id': str(transaction.id), 'msg': 'Transaction Created Successfully.'}), 200


@app.route('/transaction/update', methods=['POST'])
@verify_token
@print_info
def update_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - token
        - id: transaction id
        - data: json containing fields to update
    :param person: the person making the request
    :return: returns a transaction id used to link items to the transaction
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    transaction_id = request_data.get('id')
    transaction_data = request_data.get('data')

    if transaction_id is None or transaction_data is None:
        return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

    # query the transaction
    transaction = Transaction.objects.get(id=transaction_id)

    # perform a deep copy of the old transaction
    transaction_new = Transaction(**transaction)  # TODO - this may not work, may need to copy another way

    # query the group to make sure it exists
    group_id = transaction.group
    group = Group.objects.get(id=group_id)

    # make sure the user belongs to the group
    if person.sub not in group.members:
        return jsonify({'msg': 'Token is unauthorized.'}), 404

    # make sure user is authorized
    if not (
            group.settings.admin_overrule_transaction and group.admin == person.sub
    ) and not (
            group.settings.only_owner_modify_transaction
            and transaction.created_by == person.sub
    ):
        return jsonify({'msg': 'Token is unauthorized.'}), 404

    # delete the previous transaction and unlink it from the group
    group.restricted.transactions.remove(transaction_id)
    _delete_transaction(group, transaction)

    # save the new transaction
    transaction_new.save()

    if 'who_paid' in transaction_data:
        transaction_new.who_paid = transaction_data['who_paid']

    # init transaction deltas
    balance_deltas = {}
    for p1 in group.members:
        balance_deltas[p1] = {}
        for p2 in group.members:
            if p1 != p2:
                balance_deltas[p1][p2] = 0
    transaction_new.balance_deltas = balance_deltas
    transaction_new.save()

    # init the ledger deltas
    for p in group.members:
        if p in transaction_new.who_paid:
            transaction_new.ledger_deltas[p] = transaction.who_paid[p]
        else:
            transaction_new.ledger_deltas[p] = 0
    transaction_new.save()

    # add it to the group
    group.transactions.append(transaction_new.id)
    group.save()

    # update the fields from the original transaction within the new transaction
    for k, v in transaction_data.items():
        # if the key is equal to items that should not be modified, ignore it
        if k in ['group', 'date_created', 'created_by', 'date_modified', 'modified_by', 'total_price']:
            continue
        # if user re-writing items
        elif k == 'items':
            # add the new transaction items
            for transaction_item in v:
                # this assumes the user will pass the item information in the item field rather than the id
                _add_item_to_transaction(person, transaction_new,
                                         quantity=transaction_item['quantity'],
                                         person_id=transaction_item['person'],
                                         name=transaction_item['item']['name'],
                                         desc=transaction_item['item']['desc'],
                                         unit_price=transaction_item['item']['unit_price'])
                transaction_new.reload()

        # if normal string field
        else:
            # TODO - cross our fingers this will work
            transaction_new[k] = v

    # update the last modified by
    transaction_new.modified_by = person.sub
    transaction_new.date_modified = datetime.datetime.now(datetime.timezone.utc)

    # save the transaction
    transaction_new.save()

    return jsonify({'id': transaction_new.id, 'msg': 'Transaction updated.'}), 200


@app.route('/transaction/delete', methods=['POST'])
@verify_token
@print_info
def delete_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - token
        - id: transaction id
    :param person: the person making the request
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    transaction_id = request_data.get('id')

    if transaction_id is None:
        return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

    # query the transaction
    transaction = Transaction.objects.get(id=transaction_id)
    group_id = transaction.group

    # query the group to make sure it exists
    group = Group.objects.get(id=group_id)

    # make sure the user belongs to the group
    if person.sub not in group.members:
        return jsonify({'msg': 'Token is unauthorized.'}), 404

    # make sure user is authorized
    if (
            not (
                    group.restricted.permissions.admin_overrule_delete_transaction
                    and group.admin == person.sub
            )
            and not group.settings.user_delete_transaction
            and not (
            group.settings.only_owner_delete_transaction
            and transaction.created_by == person.sub
    )
    ):
        return jsonify({'msg': 'Token is unauthorized.'}), 404

    # check if transaction is the group
    if transaction_id not in group.transactions:
        return jsonify({'msg': 'Token is unauthorized.'}), 404

    # remove the transaction from the group
    group.transactions.remove(transaction_id)

    # delete the transaction
    _delete_transaction(group, transaction)

    return jsonify({'msg': 'Transaction deleted.'}), 200


def _delete_transaction(group, transaction):
    """
    helper to delete transaction from db
    """
    # get data from the transaction
    balance_deltas = transaction.balance_deltas
    ledger_deltas = transaction.ledger_deltas
    people_involved = balance_deltas.keys()

    # revert ledger and balances
    for p1 in people_involved:
        for p2 in people_involved:
            if p1 != p2:
                group.restricted.balances[p1][p2] -= balance_deltas[p1][p2]
        group.restricted.ledger[p1] -= ledger_deltas[p1]

    # iterate through all transaction items
    for transaction_item in transaction.items:
        # get the item id
        item_id = transaction_item.item_id

        # try to get the item
        item = Item.objects(id=item_id)
        if len(item) == 0:
            continue
        item = item.first()

        # delete the item
        _delete_item(item)

    group.save()
    # delete the transaction
    transaction.delete()


def _delete_item(item):
    """
    unlink an item and delete if necessary
    """
    # decrement the items usage count
    item.usage_count -= 1

    # if the usage count is 0 delete it
    if item.usage_count <= 0:
        item.delete()
    else:
        item.save()


def _add_item_to_transaction(person, transaction, quantity, person_id, name, desc, unit_price):
    """
    helper function to add item to transaction
    """
    # get the group id
    group_id = transaction.group

    # query the group to make sure it exists
    group = Group.objects.get(id=group_id)

    # get what person id the transaction item will belong to
    sub = person_id if person_id is not None else person.sub

    # make sure the user belongs to the group
    if person.sub not in group.members or sub not in group.members:
        raise Exception('Person does not belong to group')

    # check quantity for proper value
    if quantity < 1:
        raise Exception('Quantity cannot be less than 1.')

    # query the item to make sure it exists
    item = _create_item(name, desc, unit_price)
    item_cost = item.unit_price * quantity

    # create the transaction item
    transaction_item = TransactionItem(item_id=str(item.id),
                                       person=sub,
                                       quantity=quantity,
                                       item_cost=item_cost)

    # add the transaction item to the transaction
    transaction.items.append(transaction_item)

    # save the transaction
    transaction.save()

    # increment usage count
    item.usage_count += 1

    # save the item
    item.save()

    # increment the ledger and the balance
    who_paid = transaction.who_paid
    ledger_deltas = transaction.ledger_deltas
    balance_deltas = transaction.balance_deltas

    # deduct how much the person used from the ledger deltas
    ledger_deltas[sub] -= item_cost

    # iterate through everyone that has paid in this transaction
    # this is so we can calculate who owes what in this transaction
    for p_paid in who_paid.keys():
        paid = ledger_deltas[p_paid]
        used = ledger_deltas[sub]

        # if person that paid is not the user
        if p_paid != sub:
            # if the person used more than the have paid in this transaction
            if used < 0:
                # if the amount paid is greater than the amount used
                if used + paid > 0:
                    balance_deltas[p_paid][sub] -= used
                    balance_deltas[sub][p_paid] += used
                # if the amount paid is equal to or less than the amount used
                else:
                    paid = paid if paid > 0 else -paid
                    balance_deltas[p_paid][sub] += paid
                    balance_deltas[sub][p_paid] -= paid

    transaction.ledger_deltas = ledger_deltas
    transaction.balance_deltas = balance_deltas
    transaction.save()

    # # update group with the ledger deltas
    # for k, v in ledger_deltas.items():
    #     group.restricted.ledger[k] += v
    #
    # # update group with the balance deltas
    # for p1, d in balance_deltas.items():
    #     for p2, v in d.items():
    #         group.restricted.balances[p1][p2] += v

    # group.save()
#
#
# @app.route('/transaction/remove-item', methods=['POST'])
# @verify_token
# @print_info
# def remove_item_from_transaction(person):
#     """
#     Create a transaction in the group
#     request must contain:
#         - token
#         - id: transaction id
#         - data: transaction item to delete
#     :param person: the person making the request
#     """
#
#     # get the request data
#     request_data = request.get_json(force=True, silent=True)
#     transaction_id = request_data.get('id')
#     transaction_item = request_data.get('data')
#
#     if transaction_id is None or transaction_item is None:
#         return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400
#
#     # query the transaction
#     transaction = Transaction.objects.get(id=transaction_id)
#
#     # get the transaction item and delete it
#     transaction_item = transaction.items.objects.get(**transaction_item)
#
#     # delete the item or decrement its count
#     item = Item(id=transaction_item.item_id)
#     _delete_item(item)
#
#     # delete the transaction item
#     transaction_item.delete()
#
#     # update the last modified by
#     transaction.modified_by = person.sub
#     transaction.date_modified = datetime.datetime.now(datetime.timezone.utc)
#
#     # save transaction
#     transaction.save()
#
#     return jsonify({'msg': 'Transaction updated.'}), 200


@app.route('/transaction/info', methods=['POST'])
@verify_token
@print_info
def get_transaction(person):
    """
    get a transaction in the group
    request must contain:
        - id: transaction id
    :param person: the person making the request
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    transaction_id = request_data['id']

    # query the transaction
    transaction = Transaction.objects.get(id=transaction_id)
    group_id = transaction.group

    # query the group to make sure it exists
    group = Group.objects.get(id=group_id)

    # make sure the user belongs to the group
    if person.sub not in group.members:
        return jsonify({'msg': 'Token is unauthorized or transaction does not exist.'}), 404

    return jsonify({'msg': 'Retrieved transaction.', 'data': transaction}), 200


@app.route('/receipt/add', methods=['POST'])
@verify_token
@print_info
def add_receipt(person):
    """
    Create a receipt item and attach to transaction
    request must contain:
        - token
        - id: transaction id
        - receipt: receipt image bytes string
    :param person: the person making the request
    """
    # need token, transactionID, receipt

    # get the request data
    request_data = request.get_json(force=True, silent=True)
    transaction_id = request_data['id']

    img_data_decoded = request_data['receipt'].encode('utf-8')
    file_like = base64.b64decode(img_data_decoded)
    receiptBytes = bytearray(file_like)

    # query the transaction
    transaction = Transaction.objects.get(id=transaction_id)
    group_id = transaction.group

    # query the group to make sure it exists
    group = Group.objects.get(id=group_id)

    # make sure the user belongs to the group
    if person.sub not in group.members:
        return jsonify({'msg': 'Token is unauthorized or transaction does not exist.'}), 404

    receiptObject = Receipt()

    with tempfile.TemporaryFile() as f:
        f.write(receiptBytes)
        f.flush()
        f.seek(0)
        receiptObject.receipt.put(f)

    receiptObject.save()

    # attach receipt id to transaction and update transaction modification
    transaction.receipt = receiptObject.id
    transaction.modified_by = person.sub
    transaction.date_modified = datetime.datetime.utcnow()
    transaction.save()

    return jsonify({'id': str(receiptObject.id), 'msg': 'Receipt was successfully added.'}), 200


@app.route('/receipt/get', methods=['POST'])
@verify_token
@print_info
def get_receipt(person):
    """
    Get receipt item and return jsonified image id
    request must contain:
        - token
        - id: transaction id
    :param person: the person making the request
    """
    # need token, transactionID

    # get the request data
    request_data = request.get_json(force=True, silent=True)
    transaction_id = request_data['id']

    # query the transaction
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Exception as exp:
        return jsonify({'msg': 'An error occured when querying the transaction.'}), 500

    group_id = transaction.group
    # query the group to make sure it exists
    group = Group.objects.get(id=group_id)

    # make sure the user belongs to the group
    if person.sub not in group.members:
        return jsonify({'msg': 'Token is unauthorized or transaction does not exist.'}), 404

    receiptObject = Receipt.objects.get(id=transaction.receipt)

    receiptBytes = receiptObject.receipt.read()
    receiptb64 = base64.b64encode(receiptBytes)
    receiptString = receiptb64.decode('utf-8')

    return jsonify({'msg': 'Retrieved receipt.', 'data': receiptString}), 200


###############################################################################################################
###############################################################################################################
###############################################################################################################
## ITEM


def _create_item(name: str, desc: str, unit_price: float):
    """
    Create an item
    request must contain:
        - token
        - name
        - desc
        - unit_price
    :return: returns a item id used to link items to the transaction
    """

    # check quantity for proper value
    if unit_price <= 0:
        raise Exception('Unit price cannot be less than 0.')

    # initial declarations
    item = None

    # try to get the item if exists
    item = Item.objects(name=name,
                        desc=desc,
                        unit_price=unit_price)

    # if the item does not exist
    if len(item) == 0:
        # create the item
        item = Item(name=name,
                    desc=desc,
                    unit_price=unit_price)
    else:
        item = item.first()

    # save item
    item.save()

    return item


@app.route('/item/info', methods=['POST'])
@verify_token
@print_info
def get_item(_):
    """
    get an item
    request must contain:
        - token
        - id
    :return: returns an item
    """
    # get the request data
    request_data = request.get_json(force=True, silent=True)
    item_id = request_data['id']

    # get an item
    item = Item.objects.get(id=item_id)

    return jsonify(item), 200


###############################################################################################################
###############################################################################################################
###############################################################################################################
## MAIN

def create_app():
    return app


if __name__ == "__main__":
    app.run(debug=bool(os.environ['DEBUG']), port=5000)
