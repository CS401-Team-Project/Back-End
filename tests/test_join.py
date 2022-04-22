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

    def test_invite_through_create(self):
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

        # make sure the group has been joined and invites are clear
        response = self.do_post('/group/remove-member', {'id': self.group['_id']['$oid']}, self.header2)
        assert response.status_code == 200

        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']}, self.header1)
        assert response.status_code == 200
        assert len(response.json()['data']['members']) == 1

        # delete the group
        response = self.do_post('/group/delete', {'id': self.group['_id']['$oid']}, self.header1)
        assert response.status_code == 200

    def test_invite_through_invite(self):
        # create a group with list of invites
        data = {
            'name': 'test group name',
            'desc': 'test group description',
        }
        response = self.do_post('/group/create', {'data': data}, self.header1)
        assert response.status_code == 200
        self.group = response.json()['data']

        # join the group with the second user
        emails = [self.user2['data']['email']]
        response = self.do_post('/group/invite', {'id': self.group['_id']['$oid'], 'emails': emails}, self.header1)

        assert response.status_code == 200
        # join the group with the second user
        response = self.do_post('/group/join', {'id': self.group['_id']['$oid']}, self.header2)
        assert response.status_code == 200

        # make sure the group has been joined and invites are clear
        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']}, self.header1)
        assert response.status_code == 200
        assert len(response.json()['data']['members']) == 2
        assert len(response.json()['data']['restricted']['invite_list']) == 0

        # make sure the group has been joined and invites are clear
        response = self.do_post('/group/remove-member', {'id': self.group['_id']['$oid']}, self.header2)
        assert response.status_code == 200

        response = self.do_post('/group/info', {'id': self.group['_id']['$oid']}, self.header1)
        assert response.status_code == 200
        assert len(response.json()['data']['members']) == 1

        # delete the group
        response = self.do_post('/group/delete', {'id': self.group['_id']['$oid']}, self.header1)
        assert response.status_code == 200

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
    test.test_invite_through_create()
    test.test_invite_through_invite()
