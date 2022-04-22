import json
import os
import sys
import base64
import requests
import subprocess

TRANSACTION_ID = 0
RECEIPT_STRING = ''


class Tests(object):
    """
    Unit tests for the Back-End.
    """

    global TRANSACTION_ID
    global RECEIPT_STRING

    def display_help(self):
        print("TODO: write help section")

    @classmethod
    def setup_class(cls):
        """
        This method is run once before any of the class' test methods are run.
        It sets up the environment for the tests, and checks that the token is provided and the API is up.
        """
        args_list1 = [
            '-i', '-I',
            '--i', '--I'
        ]

        args_list2 = [
            '-h', '-H',
            '--h', '--H'
                   '-help', '-Help',
            '--help', '--Help'
        ]

        for arg in sys.argv:

            # integrated, run shell through local shell
            if arg in args_list1:
                pass

            # display help
            if arg in args_list2:
                return Tests.display_help()

        cls.base_url = 'http://localhost:5000'

        # Verify that the API is up and running
        try:
            response = requests.get(f'{cls.base_url}/test_get')
            is_api_ok = response.status_code == 200
        except requests.exceptions.ConnectionError:
            is_api_ok = False

        assert is_api_ok, '/test_get endpoint reported a Connection Error. Is the API running?'

        token_file: str = 'tokens/token.txt'
        assert os.path.isfile(token_file), f'Token file not found ({token_file}). ' \
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

        # run all tests
        for file in os.listdir('./'):
            if file != 'start_test.py':
                subprocess.run(['pytest', file, '-v'])

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

    @classmethod
    def do_post(cls, endpoint, data):
        """
        test
        :return:
        """
        return requests.post(
            f'{cls.base_url}{endpoint}', json=data, headers=cls.header
        )
