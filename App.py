"""
Main api request endpoint
"""

import array
import datetime
import os
from copy import deepcopy
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

from Models import Person, Group, Item, TransactionItem, Transaction

debug = os.environ['DEBUG']

# setup the Flask server
app = Flask(__name__)

# If on debug allow cross-origin resource sharing
if bool(os.environ['DEBUG']):
    CORS(app)

app.config['MONGODB_SETTINGS'] = {
    'host': os.environ['MONGO_HOST'],
    'username': os.environ['API_USERNAME'],
    'password': os.environ['API_PASSWORD'],
    'authSource': 'smart-ledger',
    'db': 'smart-ledger'
}

db = MongoEngine()
db.init_app(app)


###############################################################################################################
###############################################################################################################
###############################################################################################################
# TEST API ENDPOINT
# TODO - this should only be available in debug

@app.route("/test_get", methods=['GET'])
def test_get():
    """
    Just a test route to verify that the API is working.
    :return: Smart Ledger API Endpoint: OK
    """
    print(f"ROUTE test: {request}")
    return "Smart Ledger API Endpoint: OK", 200


@app.route("/test_post", methods=['POST'])
def test_post():
    """
    Just a test route to verify that the API is working.
    :return: Smart Ledger API Endpoint: OK
    """
    print(f"ROUTE test_post: {request}")
    request_data = request.get_json(force=True)

    try:
        n1 = float(request_data.get('n1'))
        n2 = float(request_data.get('n2'))
        op = request_data.get('op')
    except ValueError:
        return "Invalid data", 400

    if op == "add":
        return str(n1 + n2), 200
    elif op == "sub":
        return str(n1 - n2), 200
    elif op == "mul":
        return str(n1 * n2), 200
    elif op == "div":
        return str(n1 / n2), 200
    else:
        return "Unsupported operation", 501

###############################################################################################################
###############################################################################################################
###############################################################################################################
# WRAPPERS

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
            # TODO - remove this once dev is done
            if debug:
                return func(None, *args, **kwargs)

            # get the request args depending on the type of request
            request_data = {}
            if request.method == "POST":
                request_data = request.get_json(force=True)
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
            return 'Token is unauthorized or user does not exist.', 404

    return wrap


###############################################################################################################
###############################################################################################################
###############################################################################################################
## PERSON API ENDPOINTS


@app.route('/register', methods=['POST'])
def register():
    """
    used for logging in a user. creates an account if not already exists
    :return: status of the registration
    """
    try:
        # TODO - remove this once dev is done
        if debug:
            return jsonify({'msg': 'User profile successfully retrieved.'}), 200
        print('request\n', request)
        request_data = request.get_json(force=True)
        print(request_data)
        if request_data is None:
            return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400

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
            return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400

        # get the person that is returned
        person = person.first()

        # if person not in DB create them
        if person is None:
            # TODO - add email verified and handle it

            # create the person object
            person = Person(first_name=token_info['given_name'],
                            last_name=token_info['family_name'],
                            email=token_info['email'],
                            sub=token_info['sub'],
                            picture=token_info['picture'])

        # save the person object
        person.date.last_login = datetime.datetime.utcnow()
        person.save()

        # return status message
        return jsonify({'msg': 'User profile successfully retrieved.'}), 200

    except Exception as exp:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


@app.route('/user/info', methods=['POST'])
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
        print('request', request)
        request_data = request.get_json(force=True)
        print('request_data', request_data)

        # TODO - remove this once dev is done
        if debug:
            if 'sub' in request_data and request_data['sub'] is not None:
                date = {
                    'created': datetime.datetime.utcnow(),
                }
            else:
                date = {
                    'created': datetime.datetime.utcnow(),
                    'updated': datetime.datetime.utcnow(),
                    'last_login': datetime.datetime.utcnow()
                }
            person = {
                'sub': '1234abcd',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'johndoe@email.com',
                'email_verified': True,
                'picture': None,
                'date': date,
                'pay_with': {
                    'venmo': '',
                    'cashapp': '',
                    'paypal': '',
                    'preferred': 'venmo'
                },
                'msg': ' User profile successfully retrieved.'
            }
            return jsonify(person), 200

        # if sub was given to us
        if 'sub' in request_data:
            # requesting another users info
            person = Person.objects.get(sub=request_data.get('sub'))

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
            person.msg = 'User profile successfully retrieved.'
            return jsonify(person), 200

        # else return the users info
        person.msg = 'User profile successfully retrieved.'

        return jsonify(person), 200

    except Exception as exp:
        print(exp)
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


@app.route('/user/update', methods=['POST'])
@verify_token
def update_profile(person):
    """
    modify a users profile
    :param person: current logged in user
    :param data: json with key value pairs of things to set
    :return: returns json of
    """
    try:
        print(request)

        # get fields
        request_data = request.get_json(force=True, silent=True)
        profile = request_data['data']

        # TODO - remove this once dev is done
        if debug:
            return jsonify({'msg': 'User account update.'}), 500

        # check for unallowed fields
        if set(profile.keys()).union({'email', 'sub', 'date_joined', 'picture', 'groups'}):
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
        person.date.updated = datetime.datetime.utcnow()
        person.save()
        return jsonify({'msg': 'User account update.'}), 500
    except Exception:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


@app.route('/user/delete', methods=['POST'])
@verify_token
def delete_profile(person):
    """
    delete a users profile
    :param person: current logged in user
    :return: returns json of
    """
    try:
        # TODO - remove this once dev is done
        if debug:
            return jsonify({'msg': 'User profile successfully deleted.'}), 500

        # unlink person from all groups
        # TODO - we need to figure out a policy to show users past transactions after their account has been deleted
        for group in person.groups:
            try:
                group.people.remove(person.sub)
            except Exception:
                pass

        # delete the person from the database
        person.delete()
        return jsonify({'msg': 'User profile successfully deleted.'}), 500
    except Exception as exp:
        return jsonify({'msg': exp}), 500


###############################################################################################################
###############################################################################################################
###############################################################################################################
## GROUP API ENDPOINTS

###############################################################################################################
## GROUP CREATION/DELETION

@app.route('/group/create', methods=['POST'])
@verify_token
def create_group(person):
    """
    Create a group add the creator to the group
    request must contain:
        - token
        - name: group name
        - desc: [optional]
    :param person: the person making the request
    :return: returns json with group id and msg
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)

        # TODO - remove this once dev is done
        if debug:
            group = {
                'name': 'example group',
                'desc': 'example group description.',
                'admin': '1234abcd',
                'members': ['1234abcd', 'laksdjfl2', 'i232kjhsx', 'ai232j22'],
                'restricted': {
                    'permissions': {
                        'only_admin_remove_user': True,
                        'only_owner_modify_transaction': True,
                        'admin_overrule_modify_transaction': True,
                        'user_delete_transaction': True,
                        'only_owner_delete_transaction': True,
                        'admin_overrule_delete_transaction': True
                    },
                    'balance': 0,
                    'transactions': ['213lknsdf', 'klsj234kn', 'askldfj2n', 'kjlsju2'],
                    'date': {
                        'created': datetime.datetime.utcnow(),
                        'updated': datetime.datetime.utcnow(),
                        'last_refreshed': datetime.datetime.utcnow()
                    }
                },
                'msg': 'Created group.'
            }

            return jsonify(group), 200

        data = request_data.get('data', default=None)
        if 'name' not in data:
            return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400

        group_name = data['name']
        group_desc = data.get('desc', default='')
        members = data.get('members')

        # create the group
        group = Group(name=group_name, desc=group_desc, admin=person.id)

        # add the creating user to the group
        group.members.append(person.sub)

        # save the group
        group.save()

        # add the groups id to the persons list of groups
        person.groups.append(group.id)

        # save the person object
        person.date.updated = datetime.datetime.utcnow()
        person.save()

        # TODO - finish this when invites are implemented
        if members is not None:
            if type(members) is not array:
                return jsonify({'msg': 'Missing Required Field(s) / Invalid Type(s).'}), 400
            for member in members:
                pass
        group.save()
        group.msg = 'Created group.'
        return jsonify(group), 201

    except Exception as exp:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


@app.route('/group/delete', methods=['POST'])
@verify_token
def delete_group(person):
    """
    Create a group add the creator to the group
    request must contain:
        - token
        - id: group id
    :param person: the person making the request
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data['id']

        # TODO - remove this once dev is done
        if debug:
            return jsonify({'msg': 'Group successfully deleted.'}), 200

        # query the group
        group = Group.objects(id=group_id)
        if len(group) == 0 or person.sub != group.admin:
            return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404

        group = group.first()

        # Iterate through people and unlink them from the groups
        for p_sub in group.members:

            # try to get the person from the DB
            try:
                person = Person.objects.get(sub=p_sub)
            except Exception:
                continue

            # try to remove person from group
            try:
                person.groups.remove(group_id)
                person.date.updated = datetime.datetime.utcnow()
                person.save()
            except Exception:
                continue

        # iterate through transactions and items to decrement the item counts. waiting on items to be implemented
        for t_id in group.transactions:
            # try to get the transaction
            try:
                transaction = Transaction.objects.get(id=t_id)
                _delete_transaction(transaction)
            except Exception:
                continue

        return jsonify({'msg': 'Group successfully deleted.'}), 200

    except Exception:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


@app.route('/group/info', methods=['POST'])
@verify_token
def get_group(person):
    """
    Return a group the user is in
    request must contain:
        - token
        - id: group id
    :param person: the person making the request
    :return: returns json with group id and msg
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data.get['id']

        # TODO - remove this once dev is done
        if debug:
            group = {
                'name': 'example group',
                'desc': 'example group description.',
                'admin': '1234abcd',
                'members': ['1234abcd', 'laksdjfl2', 'i232kjhsx', 'ai232j22'],
                'restricted': {
                    'permissions': {
                        'only_admin_remove_user': True,
                        'only_owner_modify_transaction': True,
                        'admin_overrule_modify_transaction': True,
                        'user_delete_transaction': True,
                        'only_owner_delete_transaction': True,
                        'admin_overrule_delete_transaction': True
                    },
                    'balance': 0,
                    'transactions': ['213lknsdf', 'klsj234kn', 'askldfj2n', 'kjlsju2'],
                    'date': {
                        'created': datetime.datetime.utcnow(),
                        'updated': datetime.datetime.utcnow(),
                        'last_refreshed': datetime.datetime.utcnow()
                    }
                },
                'msg': 'An unexpected error occurred.'
            }

            return jsonify(group), 200

        # get the group
        group = Group(id=group_id)

        # check if user is in group
        if person.sub not in group.members:
            group.restricted = None

        # return the group
        return jsonify(group), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/group/update', methods=['POST'])
@verify_token
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

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data.get('id')
        data = request_data.get('data')

        # TODO - remove this once dev is done
        if debug:
            return jsonify({'msg': 'Group updated.'}), 200

        # get the group
        group = Group.objects(id=group_id)
        if len(group) == 0:
            return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404
        group = group.first()

        # check if user is in group
        if person.sub not in group.people:
            return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404

        # weed out bad fields
        if not set(data.keys()).union({'name', 'description', 'restricted'}):
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

        group.date.update = datetime.datetime.utcnow()

        # save the group
        group.save()

        # return the group
        return jsonify({'msg': 'Group updated.'}), 200

    except Exception as exp:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


###############################################################################################################
## GROUP MEMBER ADD/REMOVE


@app.route('/group/join', methods=['POST'])
@verify_token
def join_group(person):
    """
    Add a member to the group
    request must contain:
        - token
        - id: group id
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data.get('id')

        #TODO - remove after dev
        if debug:
            return jsonify({'msg': 'User joined group.'}), 200

        # query the group
        group = Group.objects(id=group_id)
        if len(group) == 0:
            return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404
        group = group.first()

        # check if already a member
        if person.sub in group.members:
            return jsonify({'msg': 'User is already a member of the group.'}), 409

        # TODO - need to verify if invited

        # add person to group
        group.people.append(person.sub)
        group.updated = datetime.datetime.utcnow()

        # save group
        group.save()

        # link group to member
        person.groups.append(group.id)

        # save person
        person.date.updated = datetime.datetime.utcnow()
        person.save()

        return jsonify({'msg': 'User joined group.'}), 200

    except Exception:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


@app.route('/group/remove-member', methods=['POST'])
@verify_token
def remove_member(person):
    """
    Add a member to the group
    request must contain:
        - token
        - id: group id
        - userid: [optional] user to remove from the grou
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data.get('id')
        sub = request_data.get('userid')

        #TODO - remove after dev
        if debug:
            return jsonify({'msg': 'Member successfully removed.'}), 200

        # query the group
        group = Group.objects(id=group_id)
        if len(group) == 0:
            return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404
        group = group.first()

        # if the user is trying to delete another user in the group
        if sub is not None:
            # check if authorized to remove member
            if (group.settings.only_admin_remove_user and group.admin != person.sub) or sub == group.admin:
                return jsonify({'msg': 'Token is unauthorized or group does not exist.'}), 404

        else:
            # if person is trying to delete themselves from the group
            sub = person.sub

        # check if the given sub is not in group
        if sub not in group.people:
            return jsonify({'msg': 'User is not a member of the group.'}), 409

        # remove the person from the group
        group.people.remove(sub)

        # save the group
        group.updated = datetime.datetime.utcnow()
        group.save()

        # if group is tied to person object
        if group_id in person.groups:
            # remove group from person
            person.groups.remove(group_id)

            # save person
            person.date.updated = datetime.datetime.utcnow()
            person.save()

        return jsonify({'msg': 'Member successfully removed.'}), 200

    except Exception:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


@app.route('/group/refresh-id', methods=['POST'])
@verify_token
def refresh_id(person):
    """
    refreshes the group id
    request must contain:
        - token
        - id: group id
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data.get('id')

        # TODO - remove after dev
        if debug:
            return jsonify({'msg': "Group's unique identifier successfully refreshed.", 'id': 'akjlsjdflaksjdf'}), 200

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

        # TODO - need to update all links in person and Transaction DB

        # update times
        time = datetime.datetime.utcnow()
        group.updated = time
        group.last_refreshed = time

        # save the group
        group.save()
        old_group.delete()
        return jsonify({'msg': "Group's unique identifier successfully refreshed.", 'id': group.id}), 200

    except Exception:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


###############################################################################################################
###############################################################################################################
###############################################################################################################
## TRANSACTIONS


@app.route('/transaction/create', methods=['POST'])
@verify_token
def create_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - token
        - id: group id
        - title: transaction title required
        - desc: optional
        - vendor: optional
        - date: optional
    :param person: the person making the request
    :return: returns a transaction id used to link items to the transaction
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data.get('group', default=None)
        title = request_data.get('title', default=None)
        desc = request_data.get('id', default='')
        vendor = request_data.get('vendor', default='')
        date = request_data.get('date', default=datetime.datetime.utcnow)

        # TODO - remove after dev
        if debug:
            return jsonify({'id': 'aksdjjekr', 'msg': 'User added to group.'}), 200

        if group_id is None or title is None:
            return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

        # query the group to make sure it exists
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            return jsonify({'msg': 'Token is unauthorized.'}), 404

        # create the transaction
        transaction = Transaction(title=title,
                                  group=group_id,
                                  desc=desc,
                                  vendor=vendor,
                                  created_by=person.sub,
                                  modified_by=person.sub,
                                  date_purchased=date)

        # save the transaction
        transaction.save()

        # append the transaction to the group
        group.transactions.append(transaction.id)

        # save the group
        group.save()

        return jsonify({'id': transaction.id, 'msg': 'User added to group.'}), 200

    except Exception:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


# TODO update to replace transaction items
@app.route('/transaction/update', methods=['POST'])
@verify_token
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
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        transaction_id = request_data.get('id', default=None)
        transaction_new = request_data.get('data', default=None)

        if transaction_id is None or transaction_new is None:
            return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

        # query the transaction
        transaction = Transaction.objects.get(id=transaction_id)
        group_id = transaction.group

        # query the group to make sure it exists
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            return jsonify({'msg': 'Token is unauthorized.'}), 404

        # make sure user is authorized
        if not (group.settings.admin_overrule_transaction and group.admin == person.sub):
            if not (group.settings.only_owner_modify_transaction and transaction.created_by == person.sub):
                return jsonify({'msg': 'Token is unauthorized.'}), 404

        # update the transaction
        for k, v in transaction_new.items():
            # if the key is equal to items that should not be modified, ignore it
            if k in ['group', 'date_created', 'created_by', 'date_modified', 'modified_by', 'total_price']:
                continue
            # if user re-writing items
            elif k == 'items':
                # clear all previous transaction items
                for transaction_item in transaction.items:
                    _delete_item(transaction_item.item_id)
                transaction.items.clear()

                # add the new transaction items
                for transaction_item in v:
                    # TODO - probably find a better way
                    # this assumes the user will pass the item information in the item field rather than the id
                    _add_item_to_transaction(person, transaction,
                                             quantity=transaction_item.quantity,
                                             person_id=transaction_item.person,
                                             name=transaction_item.item.name,
                                             desc=transaction_item.item.desc,
                                             unit_price=transaction_item.item.unit_price)
            # if normal string field
            else:
                transaction[k] = v

        # update the last modified by
        transaction.modified_by = person.sub
        transaction.date_modified = datetime.datetime.utcnow()

        # save the transaction
        transaction.save()

        return jsonify({'id': transaction.id, 'msg': 'Transaction updated.'}), 200

    except Exception as exp:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


@app.route('/transaction/delete', methods=['POST'])
@verify_token
def delete_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - token
        - id: transaction id
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        transaction_id = request_data.get('id', default=None)

        if transaction_id is None:
            return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

        # query the transaction
        transaction = Transaction.objects.get(id=transaction_id)
        group_id = transaction.group

        # query the group to make sure it exists
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            return jsonify({'msg': 'Token is unauthorized.'}), 404

        # make sure user is authorized
        if not (group.settings.admin_overrule_delete_transaction and group.admin == person.sub):
            if not group.settings.user_delete_transaction:
                if not (group.settings.only_owner_delete_transaction and transaction.created_by == person.sub):
                    return jsonify({'msg': 'Token is unauthorized.'}), 404

        # check if transaction is the group
        if transaction_id not in group.transactions:
            return jsonify({'msg': 'Token is unauthorized.'}), 404

        # remove the transaction from the group
        group.transactions.remove(transaction_id)

        # delete the transaction
        _delete_transaction(transaction)

        return jsonify({'msg': 'Transaction deleted.'}), 200

    except Exception:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


def _delete_transaction(transaction):
    """
    helper to delete transaction from db
    """
    # iterate through all transaction items
    for transaction_item in transaction.items:
        # get the item id
        item_id = transaction_item.item_id

        # try to get the item
        item = Item.objects.get(id=item_id)

        # delete the item
        _delete_item(item)

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


@app.route('/transaction/add-item', methods=['POST'])
@verify_token
def add_item_to_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - token
        - id: transaction id
        - name: name of item
        - quantity
        - desc: desc of item
        - unit_price: unit price of item
        - person: sub of the person this transaction item belongs to (if absent it will use the passed persons is)
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        transaction_id = request_data.get('id', default=None)
        quantity = request_data.get('quantity', default=None, type=int)
        person_id = request_data.get('person', default=None)

        # get the item data from the request
        name = request_data.get('name', default=None)
        desc = request_data.get('desc', default='')
        unit_price = request_data.get('unit_price', default=None, type=float)

        if transaction_id is None or quantity is None or person_id is None or \
                name is None or unit_price is None:
            return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

        # query the transaction
        transaction = Transaction.objects.get(id=transaction_id)

        # add the item to the transaction
        _add_item_to_transaction(person, transaction, quantity, person_id, name, desc, unit_price)

        return jsonify({'id': transaction.id, 'msg': 'Transaction updated.'}), 200

    except Exception as exp:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


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
    if person.sub not in group.people or sub not in group.people:
        raise Exception('Person does not belong to group')

    # check quantity for proper value
    if quantity < 1:
        raise Exception('Quantity cannot be less than 1.')

    # query the item to make sure it exists
    item = _create_item(name, desc, unit_price)

    # create the transaction item
    transaction_item = TransactionItem(item_id=item.id,
                                       person=sub,
                                       quantity=quantity,
                                       item_cost=item.unit_price * quantity)

    # add the transaction item to the transaction
    transaction.items.append(transaction_item)

    # save the transaction
    transaction.save()

    # increment usage count
    item.usage_count += 1

    # save the item
    item.save()


@app.route('/transaction/remove-item', methods=['POST'])
@verify_token
def remove_item_from_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - token
        - id: transaction id
        - data: transaction item to delete
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        transaction_id = request_data.get('id', default=None)
        transaction_item = request_data.get('data', default=None)

        if transaction_id is None or transaction_item is None:
            return jsonify({'msg': 'Missing required field(s) or invalid type(s).'}), 400

        # query the transaction
        transaction = Transaction.objects.get(id=transaction_id)

        # get the transaction item and delete it
        transaction_item = transaction.items.objects.get(**transaction_item)

        # delete the item or decrement its count
        item = Item(id=transaction_item.item_id)
        _delete_item(item)

        # delete the transaction item
        transaction_item.delete()

        # update the last modified by
        transaction.modified_by = person.sub
        transaction.date_modified = datetime.datetime.utcnow()

        # save transaction
        transaction.save()

        return jsonify({'msg': 'Transaction updated.'}), 200

    except Exception as exp:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


@app.route('/transaction/info', methods=['POST'])
@verify_token
def get_transaction(person):
    """
    get a transaction in the group
    request must contain:
        - token
        - id: transaction id
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        transaction_id = request_data['id']

        # query the transaction
        transaction = Transaction.objects.get(id=transaction_id)
        group_id = transaction.group

        # query the group to make sure it exists
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            return jsonify({'msg': 'Token is unauthorized or transaction does not exist.'}), 404

        return jsonify(transaction), 200

    except Exception:
        return jsonify({'msg': 'An unexpected error occurred.'}), 500


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
    try:
        item = Item.objects.get(name=name,
                                desc=desc,
                                unit_price=unit_price)
    except Exception:
        pass

    # if the item does not exist
    if item is None:
        # create the item
        item = Item(name=name,
                    desc=desc,
                    unit_price=unit_price)

    # save item
    item.save()

    return item


@app.route('/item/info', methods=['POST'])
@verify_token
def get_item(_):
    """
    get an item
    request must contain:
        - token
        - id
    :return: returns an item
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        item_id = request_data['id']

        # get an item
        item = Item.objects.get(id=item_id)

        return jsonify(item), 500
    except Exception as exp:
        return jsonify({'msg': exp}), 500


###############################################################################################################
###############################################################################################################
###############################################################################################################
## MAIN


if __name__ == "__main__":
    app.run(debug=bool(os.environ['DEBUG']), port=5000)
