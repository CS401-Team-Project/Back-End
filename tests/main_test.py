import json
import os
import base64
import requests

TRANSACTION_ID = 0
RECEIPT_STRING = ""


class Tests:
    """
    Unit tests for the Back-End.
    """

    @classmethod
    def setup_class(cls):
        """
        This method is run once before any of the class' test methods are run.
        It sets up the environment for the tests, and checks that the token is provided and the API is up.
        """

        cls.base_url = 'http://localhost:5000'
        # self.base_url = 'http://ddns.absolutzero.org:5555'

        # Verify that the API is up and running
        try:
            response = requests.get(f'{cls.base_url}/test_get')
            is_api_ok = response.status_code == 200
        except requests.exceptions.ConnectionError:
            is_api_ok = False

        assert is_api_ok, '/test_get endpoint reported a Connection Error. Is the API running?'

        token_file: str = 'token.txt'
        assert os.path.isfile(token_file) == True, f'Token file not found ({token_file}). ' \
                                                   f'Please create this file and fill it with your ' \
                                                   f'OAuth token from Front-End.'

        # Read token from file and assign it to the header of the requests
        with open(token_file, 'r') as file:
            token = file.readline().strip()
            cls.header = {'Authorization': f'Bearer {token}'}

        # need to set up user stuff here for use later
        response = cls.do_post('/register', {})

        cls.user = response.json()
        cls.group = None

    @classmethod
    def teardown_class(cls):
        """teardown any state that was previously setup with a call to
        setup_class.
        """
        pass

    def ensure_status_code_msg(self, response, correct_status_code, correct_msg):
        data = response.json()
        cond_1 = response.status_code == correct_status_code
        cond_2 = data['msg'] == correct_msg
        assert cond_1 and cond_2, f"Expected status code {correct_status_code} with msg `{correct_msg}`, " \
                                  f"got {response.status_code} with msg `{data['msg']}`"

    def create_group(self, data):
        return self.do_post('/group/create', {'data': data})

    def test_get(self):
        """
        test
        :return:
        """
        response = requests.get(f'{self.base_url}/test_get')
        self.ensure_status_code_msg(response, 200, "Smart Ledger API Endpoint: OK")

    def test_delete_and_register(self):
        """
        test
        :return:
        """
        # delete
        response = self.do_post('/user/delete', {'sub': self.user['data']['sub']})
        self.ensure_status_code_msg(response, 200, "Successfully deleted the user profile.")

        # try to delete second time to ensure 404 is returned
        response = self.do_post('/user/delete', {'sub': self.user['data']['sub']})
        self.ensure_status_code_msg(response, 404, "Token is unauthorized or user does not exist.")
        
        # register new user for status_code 201
        response = self.do_post('/register', {})
        self.ensure_status_code_msg(response, 201, "User successfully retrieved.")
        assert response.json()['data']['sub'] == self.user['data']['sub']

        # try second register for status_code 200
        response = self.do_post('/register', {})
        self.ensure_status_code_msg(response, 200, "User successfully retrieved.")

    def test_bad_payment(self):
        """
        test
        :return:
        """
        response = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        self.ensure_status_code_msg(response, 200, "User successfully retrieved.")

        # assign preferred value as an option that hasn't been set
        data = {
            'pay_with': {
                'venmo': 'test venmo',
                'paypal': 'test paypal',
                'preferred': 'cashapp'
            }
        }
        response = self.do_post('/user/update', {'data': data})
        self.ensure_status_code_msg(response, 400, "Missing Required Field(s) / Invalid Type(s).")

        # assign nonsense as 'pay_with' parameter
        data = {
            'pay_with': {
                'bad': 'data'
            }
        }
        response = self.do_post('/user/update', {'data': data})
        self.ensure_status_code_msg(response, 500, "An unexpected error occurred.")

    def test_user_info(self):
        """
        test
        :return:
        """
        # test legitimate sub
        response = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        self.ensure_status_code_msg(response, 200, "User successfully retrieved.")

        # test fake sub
        response = self.do_post('/user/info', {'sub': 'baddatabaddatawhatchagonnado'})
        self.ensure_status_code_msg(response, 404, "Token is unauthorized or user does not exist.")

        # test update pay with
        data = {
            'pay_with': {
                'venmo': 'test venmo',
                'cashapp': 'test cashapp',
                'paypal': 'test paypal',
                'preferred': 'venmo',
            }
        }
        response = self.do_post('/user/update', {'data': data})
        self.ensure_status_code_msg(response, 200, "Successfully updated the user profile.")

        # check changes
        response = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        self.ensure_status_code_msg(response, 200, "User successfully retrieved.")
        assert response.json()['data']['pay_with'] == data['pay_with']
        
    def test_group_no_desc(self):
        """
        test
        :return:
        """

        # create a group
        data = {
            'name': 'test group name',
        }
        response = self.create_group(data)
        self.group = response.json()['data']
        self.ensure_status_code_msg(response, 200, "Group successfully created.")

        # get the group
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully retrieved.")
        assert response.json()['data']['name'] == 'test group name'

        # delete the group
        response = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully deleted.")

        # check persons groups
        response = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        self.ensure_status_code_msg(response, 200, "User successfully retrieved.")
        assert self.group['_id'] not in response.json()['data']['groups']

    def test_bad_group(self):
        """
        test
        :return:
        """

        # create a group with no data
        data = {
            'bad': 'data'
        }
        response = self.create_group(data)
        self.ensure_status_code_msg(response, 400, "Missing Required Field(s) / Invalid Type(s).")

    def test_create_group(self):
        """
        test
        :return:
        """

        # create a group
        data = {
            'name': 'test group name',
            'desc': 'test group description'
        }
        response = self.create_group(data)
        self.group = response.json()['data']
        self.ensure_status_code_msg(response, 200, "Group successfully created.")

        # check that admin is assigned correctly
        assert response.json()['data']['admin'] == self.user['data']['sub']

        # get the group
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully retrieved.")
        # assert self.group == response.json()['data']

        # check persons groups
        response = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        self.ensure_status_code_msg(response, 200, "User successfully retrieved.")
        user = response.json()['data']
        assert self.group['_id'] in user['groups']

        # update normal group stuff
        data = {
            'name': 'test group update name',
            'desc': 'test group update description'
        }
        response = self.do_post('/group/update', {'id': self.group['_id']['$oid'], 'data': data})
        self.ensure_status_code_msg(response, 200, "Group successfully updated.")

        # get the group
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully retrieved.")
        assert response.json()['data']['name'] == 'test group update name'
        assert response.json()['data']['desc'] == 'test group update description'

        # delete the group
        response = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully deleted.")

        # check persons groups
        response = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        self.ensure_status_code_msg(response, 200, "User successfully retrieved.")
        assert self.group['_id'] not in response.json()['data']['groups']

    def test_add_receipt(self):
        global TRANSACTION_ID
        global RECEIPT_STRING
        # create group
        group_data = {
            'name': 'Test Receipt Group',
        }
        response = self.create_group(group_data)
        self.ensure_status_code_msg(response, 200, "Group successfully created.")

        # attach user to group
        self.group = response.json()['data']

        # check that admin is assigned correctly
        assert response.json()['data']['admin'] == self.user['data']['sub']

        # get the group
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully retrieved.")
        # assert self.group == response.json()['data']

        # create transaction
        items = [
            {
                'name': 'Borger',
                'quantity': 1,
                'desc': 'borger',
                'unit_price': 20,
                'owned_by': self.user['data']['sub']
            }
        ]

        who_paid = {
            self.user['data']['sub']: 20
        }

        transaction_data = {
            'id': self.group['_id']['$oid'],
            'title': 'Test Receipt Transaction',
            'desc': 'Test Receipt Description',
            'vendor': 'Test Receipt Vendor',
            'items': items,
            'who_paid': who_paid
        }

        response = self.do_post('/transaction/create', transaction_data)
        self.ensure_status_code_msg(response, 200, 'Transaction Created Successfully.')

        # set global variable for test_get_receipt and test_create_receipt_image
        TRANSACTION_ID = response.json()['id']

        # create receipt
        img_data = requests.get('https://freepngimg.com/download/space/24553-1-space-planet.png').content
        img_data_b64 = base64.b64encode(img_data)
        RECEIPT_STRING = img_data_b64.decode('utf-8')

        response = self.do_post('/receipt/add', {'id': TRANSACTION_ID, 'receipt': RECEIPT_STRING})
        self.ensure_status_code_msg(response, 200, "Receipt was successfully added.")

    def test_get_receipt(self):
        response = self.do_post('/receipt/get', {'id': TRANSACTION_ID})
        self.ensure_status_code_msg(response, 200, 'Retrieved receipt.')

    def test_create_receipt_image(self):
        # when using image formats other than png, change file extensions here
        # to ensure proper format
        response = self.do_post('/receipt/get', {'id': TRANSACTION_ID})
        receivedBytesString = response.json()['data'].encode('utf-8')
        file_like = base64.b64decode(receivedBytesString)
        receiptBytes = bytearray(file_like)
        with open('test_image_1.png', 'wb') as bin_file:
            bin_file.write(receiptBytes)

        file_like = base64.b64decode(RECEIPT_STRING)
        receiptBytes = bytearray(file_like)
        with open('test_image_2.png', 'wb') as bin_file:
            bin_file.write(receiptBytes)

    def test_invite(self):
        # create a group with list of invites
        invites = ['test1@email.com', 'test2@email.com', 'test3@email.com']
        data = {
            'name': 'test group name',
            'desc': 'test group description',
            'invites': invites
        }
        response = self.create_group(data)
        self.ensure_status_code_msg(response, 200, "Group successfully created.")
        self.group = response.json()['data']

        # check invites
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully retrieved.")
        assert invites == response.json()['data']['restricted']['invite_list']

        # delete the group
        response = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully deleted.")

        # create new group with no invites
        invites = data.pop('invites')
        response = self.create_group(data)
        self.ensure_status_code_msg(response, 200, "Group successfully created.")
        self.group = response.json()['data']
        assert len(self.group['restricted']['invite_list']) == 0

        # invite via the invite api call
        response = self.do_post('/group/invite', {'id': self.group['_id']['$oid'], 'emails': invites})
        self.ensure_status_code_msg(response, 200, "Invitation(s) successfully created.")

        # check invites
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully retrieved.")
        assert invites == response.json()['data']['restricted']['invite_list']

        # delete the group
        response = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group successfully deleted.")

    def test_group_refresh_id(self):
        """
        test
        :return:
        """

        # create a group
        data = {
            'name': 'test group name',
            'desc': 'test group desc',
        }
        response = self.do_post('/group/create', {'data': data})
        self.group = response.json()['data']
        self.ensure_status_code_msg(response, 200, "Group successfully created.")

        # add some extra stuff to check
        data = {
            'restricted': {
                'permissions': {
                    'admin_overrule_modify_transaction': False
                }
            }
        }
        response = self.do_post('/group/update', {'id':self.group['_id']['$oid'], 'data': data})
        self.ensure_status_code_msg(response, 200, "Group successfully updated.")

        # get new copy of group
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        self.group = response.json()['data']
        self.ensure_status_code_msg(response, 200, "Group successfully retrieved.")

        # check persons groups
        response = self.do_post('/group/refresh-id', {'id': self.group['_id']['$oid']})
        self.ensure_status_code_msg(response, 200, "Group's unique identifier successfully refreshed.")
        id = response.json()['id']

        # check to make sure id's are different and fields are the same
        response = self.do_post('/group/info', {'id': id})
        self.ensure_status_code_msg(response, 200, "Group successfully retrieved.")
        group = response.json()['data']
        assert self.group['name'] == group['name']
        assert self.group['desc'] == group['desc']
        assert self.group['restricted']['permissions']['admin_overrule_modify_transaction'] \
               == group['restricted']['permissions']['admin_overrule_modify_transaction']
        assert self.group['_id'] != group['_id']

        # delete the group
        response = self.do_post('/group/delete', {'id': id})
        self.ensure_status_code_msg(response, 200, "Group successfully deleted.")

    # This test passed, DO NOT RUN unless you want your profile deleted for the tests.
    # def test_delete_profile(self):
    #     """
    #     test
    #     :return:
    #     """
    #     # delete
    #     _, status_code = self.do_post('/user/delete', {'sub': self.user['data']['sub']})
    #     assert status_code == 200
    #
    #     # try to delete second time to ensure 404 is returned
    #     _, status_code = self.do_post('/user/delete', {'sub': self.user['data']['sub']})
    #     assert status_code == 404

    @classmethod
    def do_post(cls, endpoint, data):
        """
        test
        :return:
        """
        return requests.post(
            f'{cls.base_url}{endpoint}', json=data, headers=cls.header
        )
