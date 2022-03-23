"""
Main api request endpoint
"""
import datetime
import os
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests
from password_generator import PasswordGenerator

from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

from Models import Person, Group, Item, TransactionItem, Transaction

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


###############################################################################################################
###############################################################################################################
###############################################################################################################
# TEST API ENDPOINT
# TODO - this should only be available in debug

@app.route("/test", methods=['GET'])

def test():
    """
    Just a test route to verify that the API is working.
    :return: Smart Ledger API Endpoint: OK
    """
    print(f"ROUTE test: {request}")
    return "Smart Ledger API Endpoint: OK", 200


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
###############################################################################################################
###############################################################################################################
## PERSON API ENDPOINTS


@app.route('/person/register', methods=['POST'])
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


@app.route('/person/set', methods=['POST'])
@verify_token
def set_profile(person):
    """
    modify a users profile
    :param person: current logged in user
    :param profile: json with key value pairs of things to set
    :return: returns json of
    """
    try:
        # get fields
        request_data = request.get_json(force=True, silent=True)
        profile = request_data['profile']

        # iterate through given fields
        for k,v in profile.items():
            # if in list do nothing
            if k in ['email', 'sub', 'date_joined', 'picture', 'groups']:
                continue
            # set the keyed value
            else:
                person[k] = v

        # save the person
        person.save()
        return jsonify({'msg': 'User account deleted.'}), 500
    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/person/profile', methods=['POST'])
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


@app.route('/person/delete', methods=['POST'])
@verify_token
def delete_profile(person):
    """
    delete a users profile
    :param person: current logged in user
    :return: returns json of
    """
    try:
        # unlink person from all groups
        # TODO - we need to figure out a policy to show users past transactions after their account has been deleted
        for group in person.groups:
            try:
                group.people.remove(person.sub)
            except Exception:
                pass

        # delete the person from the database
        person.delete()
        return jsonify({'msg': 'User account deleted.'}), 500
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
        - join_code: [optional]
    :param person: the person making the request
    :return: returns json with group id and msg
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_name = request_data.get('name')
        join_code = request_data.get('join_code', default=None)

        # create a random password for joining the group
        join_code = join_code if join_code is not None else PasswordGenerator().generate()

        # create the group
        group = Group(name=group_name, admin=person.id, join_code=join_code)

        # add the creating user to the group
        group.people.append(person.sub)

        # save the group
        group.save()

        # add the groups id to the persons list of groups
        person.groups.append(group.id)

        # save the person object
        person.save()

        return jsonify({'id': group.id, 'join_code': join_code, 'msg': 'Created group'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


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
        group_id = request_data.get('id')

        # query the group
        group = Group(id=group_id)

        # check privilege
        if person.sub != group.admin:
            raise Exception("User not authorized to delete group.")

        # Iterate through people and unlink them from the groups
        for p_sub in group.people:

            # try to get the person from the DB
            try:
                person = Person.objects.get(sub=p_sub)
            except Exception:
                print('Person does not exist')
                continue

            # try to remove person from group
            try:
                person.groups.remove(group_id)
                person.save()
            except Exception:
                print('Person does not belong to group')
                continue

        # iterate through transactions and items to decrement the item counts. waiting on items to be implemented
        for t_id in group.transactions:
            # try to get the transaction
            try:
                transaction = Transaction.objects.get(id=t_id)
                _delete_transaction(transaction)
            except Exception:
                print("Transaction does not exist")
                continue

        return jsonify({'msg': 'Group Deleted'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/group/get', methods=['POST'])
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
        group_id = request_data.get('id')

        # get the group
        group = Group(id=group_id)

        # check if user is in group
        if person.sub not in group.people:
            raise Exception('User not in group')

        # if only the admin can view the join code and user is not admin, clear out the join code
        if group.settings.only_admin_view_join_code and group.admin != person.sub:
            group.join_code = None

        # add the creating user to the group
        group.people.append(person.sub)

        # return the group
        return jsonify(group), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/group/set', methods=['POST'])
@verify_token
def set_group(person):
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
        group_new = request_data.get('group')

        # get the group
        group = Group(id=group_id)

        # check if user is in group
        if person.sub not in group.people:
            raise Exception('User not in group')

        # iterate through all items
        for k, v in group_new.items():
            # if the key is the id, people, or settings ignore it
            # if the user wants to delete a transaction they should use delete_transaction
            # TODO - assign the settings here. settings must check if only admin has permissions to change this.
            if k in ['id', 'people', 'settings', 'transactions']:
                continue

            # if is join code check if authorized
            elif k == 'join_code':
                # if only the admin can view the join code and user is not admin
                if group.settings.only_admin_set_join_code and group.admin != person.sub:
                    continue
                group.join_code = v

            else:
                # TODO - test this at some point to make sure this works
                group[k] = v
        # save the group
        group.save()

        # return the group
        return jsonify({'msg': 'Group updated'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500

###############################################################################################################
## GROUP MEMBER GET/ADD/REMOVE


@app.route('/group/members', methods=['POST'])
@verify_token
def get_members(person):
    """
    Get a list of members that belong to a group
    request must contain a token and a group id
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data.get('id')

        # query the group
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            raise Exception('User does not belong to group')

        # get the members
        members = group.people

        # check if user is in the group
        if person.sub not in members:
            raise Exception('User does not belong to group.')

        return jsonify(members), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/group/join', methods=['POST'])
@verify_token
def join_group(person):
    """
    Add a member to the group
    request must contain:
        - token
        - id: group id
        - join_code
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data.get('id')
        join_code = request_data.get('join_code')

        # query the group
        group = Group.objects.get(id=group_id)

        # check if user join code is correct
        if group.join_code != join_code:
            raise Exception('Join code is not correct')

        # add person to group
        group.people.append(person.sub)

        # save group
        group.save()

        # link group to member
        person.groups.append(group.id)

        # save person
        person.save()

        return jsonify({'msg': 'User added to group.'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/group/remove_member', methods=['POST'])
@verify_token
def remove_member(person):
    """
    Add a member to the group
    request must contain:
        - token
        - id: group id
        - sub: [optional] user to remove from the grou
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data.get('id')
        sub = request_data.get('sub')

        # query the group
        group = Group.objects.get(id=group_id)

        # if the user is trying to delete another user in the group
        if sub is not None:
            # check if authorized to remove member
            if (group.settings.only_admin_remove_user and group.admin != person.sub) or sub == group.admin:
                raise Exception('User not authorized to remove member.')
        else:
            # if person is trying to delete themselves from the group
            sub = person.sub

        # check if the given sub is not in group
        if sub not in group.people:
            raise Exception('User does not belong to group.')

        # remove the person from the group
        group.people.remove(sub)

        # save the group
        group.save()

        # if group is tied to person object
        if group_id in person.groups:
            # remove group from person
            person.groups.remove(group_id)

            # save person
            person.save()

        return jsonify({'msg': 'User added to group.'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


###############################################################################################################
###############################################################################################################
###############################################################################################################
## TRANSACTIONS

# TODO - add get transaction

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
    :param person: the person making the request
    :return: returns a transaction id used to link items to the transaction
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data['id']
        title = request_data['title']
        desc = request_data.get('id', default='')
        vendor = request_data.get('vendor', default='')

        # query the group to make sure it exists
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            raise Exception('Person does not belong to group')

        # create the transaction
        transaction = Transaction(title=title,
                                  group=group_id,
                                  desc=desc,
                                  vendor=vendor,
                                  created_by=person.sub,
                                  modified_by=person.sub)

        # save the transaction
        transaction.save()

        # append the transaction to the group
        group.transactions.append(transaction.id)

        # save the group
        group.save()

        return jsonify({'id': transaction.id, 'msg': 'User added to group.'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


# TODO update to replace transaction items
@app.route('/transaction/update', methods=['POST'])
@verify_token
def update_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - token
        - id: transaction id
        - transaction: json containing fields to update
    :param person: the person making the request
    :return: returns a transaction id used to link items to the transaction
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        transaction_id = request_data['id']
        transaction_new = request_data['transaction']

        # query the transaction
        transaction = Transaction.objects.get(id=transaction_id)
        group_id = transaction.group

        # query the group to make sure it exists
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            raise Exception('Person does not belong to group')

        # make sure user is authorized
        if not (group.settings.admin_overrule_transaction and group.admin == person.sub):
            if not (group.settings.only_owner_modify_transaction and transaction.created_by == person.sub):
                raise Exception('User is not authorized to update the transaction.')

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
        return jsonify({'msg': exp}), 500


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
        transaction_id = request_data['id']

        # query the transaction
        transaction = Transaction.objects.get(id=transaction_id)
        group_id = transaction.group

        # query the group to make sure it exists
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            raise Exception('Person does not belong to group')

        # make sure user is authorized
        if not (group.settings.admin_overrule_delete_transaction and group.admin == person.sub):
            if not group.settings.user_delete_transaction:
                if not (group.settings.only_owner_delete_transaction and transaction.created_by == person.sub):
                    raise Exception('User is not authorized to update the transaction.')

        # check if transaction is the group
        if transaction_id not in group.transactions:
            raise Exception('Transaction not in group')

        # remove the transaction from the group
        group.transactions.remove(transaction_id)

        # delete the transaction
        _delete_transaction(transaction)

        return jsonify({'msg': 'Transaction deleted.'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


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

@app.route('/transaction/add', methods=['POST'])
@verify_token
def add_item_to_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - token
        - id: transaction id
        - quantity
        - name: name of item
        - desc: desc of item
        - unit_price: unit price of item
        - person: sub of the person this transaction item belongs to (if absent it will use the passed persons is)
    :param person: the person making the request
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        transaction_id = request_data['id']
        quantity = request_data['quantity']
        person_id = request_data.get('person')

        # get the item data from the request
        name = request_data.get('name')
        desc = request_data.get('desc')
        unit_price = request_data.get('unit_price')

        # query the transaction
        transaction = Transaction.objects.get(id=transaction_id)

        # add the item to the transaction
        _add_item_to_transaction(person, transaction, quantity, person_id, name, desc, unit_price)

        return jsonify({'id': transaction.id, 'msg': 'Transaction updated.'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


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


@app.route('/transaction/get', methods=['POST'])
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
            raise Exception('Person does not belong to group')

        return jsonify(transaction), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500

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


@app.route('/item/get', methods=['POST'])
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
