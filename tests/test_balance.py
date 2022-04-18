import os

import requests
from pprint import pprint


class BalanceTests:
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

        ####################################################################################
        token_file1: str = 'token.txt'
        assert os.path.isfile(token_file1) == True, f'Token file not found ({token_file1}). ' \
                                                    f'Please create this file and fill it with your ' \
                                                    f'OAuth token from Front-End.'

        # Read token from file and assign it to the header of the requests
        with open(token_file1, 'r') as file:
            token = file.readline().strip()
        cls.header1 = {'Authorization': f'Bearer {token}'}

        # need to set up user stuff here for use later
        response = cls.do_post('/register', {}, cls.header1)
        cls.user1 = response.json()
        ####################################################################################
        token_file2: str = 'token2.txt'
        assert os.path.isfile(token_file2) == True, f'Token file not found ({token_file2}). ' \
                                                    f'Please create this file and fill it with your ' \
                                                    f'OAuth token from Front-End.'

        # Read token from file and assign it to the header of the requests
        with open(token_file2, 'r') as file:
            token = file.readline().strip()
            cls.header2 = {'Authorization': f'Bearer {token}'}
        # need to set up user stuff here for use later
        response = cls.do_post('/register', {}, cls.header2)
        cls.user2 = response.json()
        ####################################################################################
        cls.group = None

    @classmethod
    def teardown_class(cls):
        """teardown any state that was previously setup with a call to
        setup_class.
        """
        pass

    def test_balance(self):
        # create a group with list of invites
        data = {
            'name': 'test group name',
            'desc': 'test group description',
            'invites': [self.user2['data']['email']]
        }
        response = self.do_post('/group/create', {'data': data}, self.header1)
        assert response.status_code == 200
        self.group = response.json()['data']

        # join the group with the second user
        response = self.do_post('/group/join', {'id': self.group['_id']['$oid']}, self.header2)
        assert response.status_code == 200

        # make sure the group has been joined and invites are clear
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']}, self.header1)
        assert response.status_code == 200
        assert len(response.json()['data']['members']) == 2
        assert len(response.json()['data']['restricted']['invite_list']) == 0

        ####################################################################################
        ## Transaction 1
        who_paid = {self.user1['data']['sub']: 20, self.user2['data']['sub']: 20}
        items = [
            {'owed_by': self.user1['data']['sub'], 'name': 'item1', 'desc': 'item1', 'unit_price': 20, 'quantity': 1},
            {'owed_by': self.user2['data']['sub'], 'name': 'item2', 'desc': 'item2', 'unit_price': 20, 'quantity': 1},
        ]
        t1 = {
            'id': self.group['_id']['$oid'],
            'title': 'transaction1',
            'who_paid': who_paid,
            'items': items
        }
        self.do_post('/transaction/create', t1, self.header1)
        assert response.status_code == 200

        # make sure the group has been joined and invites are clear
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']}, self.header1)
        assert response.status_code == 200
        assert response.json()['data']['restricted']['balances'][self.user1['data']['sub']][
                   self.user2['data']['sub']] == 0
        assert response.json()['data']['restricted']['balances'][self.user2['data']['sub']][
                   self.user1['data']['sub']] == 0

        ####################################################################################
        ## Transaction 2
        who_paid = {self.user1['data']['sub']: 40}
        items = [
            {'owed_by': self.user2['data']['sub'], 'name': 'item2', 'desc': 'item2', 'unit_price': 40, 'quantity': 1},
        ]
        t2 = {
            'id': self.group['_id']['$oid'],
            'title': 'transaction2',
            'who_paid': who_paid,
            'items': items
        }
        self.do_post('/transaction/create', t2, self.header1)
        assert response.status_code == 200

        # make sure the group has been joined and invites are clear
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']}, self.header1)
        assert response.status_code == 200
        assert response.json()['data']['restricted']['balances'][self.user1['data']['sub']][
                   self.user2['data']['sub']] == 40
        assert response.json()['data']['restricted']['balances'][self.user2['data']['sub']][
                   self.user1['data']['sub']] == -40

        ####################################################################################
        ## Transaction 3
        who_paid = {self.user2['data']['sub']: 40}
        items = [
            {'owed_by': self.user1['data']['sub'], 'name': 'item2', 'desc': 'item2', 'unit_price': 40, 'quantity': 1},
        ]
        t3 = {
            'id': self.group['_id']['$oid'],
            'title': 'transaction3',
            'who_paid': who_paid,
            'items': items
        }
        self.do_post('/transaction/create', t3, self.header1)
        assert response.status_code == 200

        # make sure the group has been joined and invites are clear
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']}, self.header1)

        assert response.status_code == 200
        assert response.json()['data']['restricted']['balances'][self.user1['data']['sub']][
                   self.user2['data']['sub']] == 0
        assert response.json()['data']['restricted']['balances'][self.user2['data']['sub']][
                   self.user1['data']['sub']] == 0
        ####################################################################################
        ## Transaction 4
        who_paid = {self.user1['data']['sub']: 40}
        items = [
            {'owed_by': self.user1['data']['sub'], 'name': 'item1', 'desc': 'item1', 'unit_price': 20, 'quantity': 1},
            {'owed_by': self.user2['data']['sub'], 'name': 'item2', 'desc': 'item2', 'unit_price': 20, 'quantity': 1},
        ]
        t4 = {
            'id': self.group['_id']['$oid'],
            'title': 'transaction4',
            'who_paid': who_paid,
            'items': items
        }
        self.do_post('/transaction/create', t4, self.header1)
        assert response.status_code == 200

        # make sure the group has been joined and invites are clear
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']}, self.header1)

        assert response.status_code == 200
        assert response.json()['data']['restricted']['balances'][self.user1['data']['sub']][
                   self.user2['data']['sub']] == 20
        assert response.json()['data']['restricted']['balances'][self.user2['data']['sub']][
                   self.user1['data']['sub']] == -20

        ####################################################################################
        ## Transaction 4
        who_paid = {self.user2['data']['sub']: 40}
        items = [
            {'owed_by': self.user1['data']['sub'], 'name': 'item1', 'desc': 'item1', 'unit_price': 20, 'quantity': 1},
            {'owed_by': self.user2['data']['sub'], 'name': 'item2', 'desc': 'item2', 'unit_price': 20, 'quantity': 1},
        ]
        t5 = {
            'id': self.group['_id']['$oid'],
            'title': 'transaction4',
            'who_paid': who_paid,
            'items': items
        }
        self.do_post('/transaction/create', t5, self.header1)
        assert response.status_code == 200

        # make sure the group has been joined and invites are clear
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']}, self.header1)

        assert response.status_code == 200
        assert response.json()['data']['restricted']['balances'][self.user1['data']['sub']][
                   self.user2['data']['sub']] == 0
        assert response.json()['data']['restricted']['balances'][self.user2['data']['sub']][
                   self.user1['data']['sub']] == 0

    @classmethod
    def do_post(cls, endpoint, data, header):
        """
        test
        :return:
        """
        return requests.post(
            f'{cls.base_url}{endpoint}', json=data, headers=header
        )


if '__main__' == __name__:
    test = BalanceTests()
    test.setup_class()
    test.test_balance()
