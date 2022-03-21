"""
Main api request endpoint
"""
import datetime
import os
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests

from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

from Models import Person, Group, Item, TransactionItem, Transaction
from password_generator import PasswordGenerator

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


@app.route('/person/user_profile', methods=['POST'])
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


@app.route('/person/get_groups', methods=['POST'])
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
    :param person: the person making the request
    :return: returns json with group id and msg
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_name = request_data.get('name')

        # create a random password for joining the group
        pwd = PasswordGenerator().generate()

        # create the group
        group = Group(name=group_name, admin=person.id, join_code=pwd)

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

        # make sure the user belongs to the group
        if person.sub not in group.people:
            raise Exception('User does not belong to group')

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
            except Exception:
                print("Transaction does not exist")
                continue

            # iterate through all transaction items
            for transaction_item in transaction.items:
                # get the item id
                item_id = transaction_item.item_id

                # try to get the item
                try:
                    item = Item.objects.get(id=item_id)
                except Exception:
                    print('item does not exist')
                    continue

                # decrement the items usage count
                item.usage_count -= 1

                # if the usage count is 0 delete it
                if item.usage_count <= 0:
                    item.delete()

        return jsonify({'msg': 'Group Deleted'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


###############################################################################################################
## JOIN CODE GET/SET


@app.route('/group/get_join_code', methods=['POST'])
@verify_token
def get_join_code(person):
    """
    Retrieve a groups join code
    request must contain:
        - token
        - id: group id
    :param person: the person making the request
    :return: returns json with group id and msg
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data['id']

        # create the group
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            raise Exception('User does not belong to group')

        # check privilege
        if group.settings.only_admin_view_join_code and group.admin != person.sub:
            raise Exception("User not authorized to view join code.")

        # get the join code
        join_code = group.join_code

        return jsonify({'join_code': join_code}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/group/set_join_code', methods=['POST'])
@verify_token
def set_join_code(person):
    """
    set a groups join code
    request must contain:
        - token
        - id: group id
        - join_code
    :param person: the person making the request
    :return: returns json with group id and msg
    """

    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        group_id = request_data['id']
        join_code = request_data['join_code']

        # create the group
        group = Group.objects.get(id=group_id)

        # make sure the user belongs to the group
        if person.sub not in group.people:
            raise Exception('User does not belong to group')

        # check privilege
        if group.settings.only_admin_set_join_code and group.admin != person.sub:
            raise Exception("User not authorized to set join code.")

        # set the join code
        group.join_code = join_code

        # save the group
        group.save()

        return jsonify({'msg': 'Join code changed'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


###############################################################################################################
## GROUP MEMBER GET/ADD/REMOVE


@app.route('/group/get_members', methods=['POST'])
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


@app.route('/group/add_member', methods=['POST'])
@verify_token
def add_member(person):
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
            # check if user join code is correct
            if group.settings.only_admin_remove_user and group.admin != person.sub:
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


@app.route('/group/create', methods=['POST'])
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

        return jsonify({'id': transaction.id, 'msg': 'User added to group.'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


@app.route('/transaction/update', methods=['POST'])
@verify_token
def update_transaction(person):
    """
    Create a transaction in the group
    request must contain:
        - token
        - id: transaction id
        - title: transaction title required
        - desc: optional
        - vendor: optional
    :param person: the person making the request
    :return: returns a transaction id used to link items to the transaction
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        transaction_id = request_data['id']
        title = request_data['title']
        desc = request_data.get('id', default='')
        vendor = request_data.get('vendor', default='')

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
        transaction.title = title
        transaction.desc = desc
        transaction.vendor = vendor

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
    :return: returns a transaction id used to link items to the transaction
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

        # delete the transaction
        transaction.delete()

        return jsonify({'id': transaction.id, 'msg': 'Transaction updated.'}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


###############################################################################################################
###############################################################################################################
###############################################################################################################
## ITEM


@app.route('/item/get', methods=['POST'])
@verify_token
def get_item(_):
    """
    Create a transaction in the group
    request must contain:
        - token
        - name
        - desc
        - unit_price
    :return: returns a transaction id used to link items to the transaction
    """
    try:
        # get the request data
        request_data = request.get_json(force=True, silent=True)
        name = request_data['name']
        desc = request_data['desc']
        unit_price = request_data['unit_price']

        # initial declarations
        item = None
        msg = 'Retrieved item.'

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
            msg = 'Created item.'
            item = Item(name=name,
                        desc=desc,
                        unit_price=unit_price)

        # increment usage count
        item.usage_count += 1

        # save item
        item.save()

        return jsonify({'id': item.id, 'msg': msg}), 200

    except Exception as exp:
        return jsonify({'msg': exp}), 500


###############################################################################################################
###############################################################################################################
###############################################################################################################
## MAIN


if __name__ == "__main__":
    app.run(debug=bool(os.environ['DEBUG']), port=5000)
