# import pytest
import requests


class Tests:
    @classmethod
    def setup_class(self):
        """setup any state specific to the execution of the given class (which
        usually contains tests).
        """

        self.base_url = 'http://localhost:5000'
        with open('token.txt') as f:
            token = f.readline()
        self.header = {
            'Authorization': f'Bearer {token}'
        }

        # need to set up user stuff here for use later
        content, _ = self.do_post('/register', {})
        self.user = content['data']

    @classmethod
    def teardown_class(self):
        """teardown any state that was previously setup with a call to
        setup_class.
        """
        pass

    def test_register(self):
        content, status_code = self.do_post('/register', {})
        assert status_code == 200

    def test_user_info(self):
        # test legitimate sub
        content, status_code = self.do_post('/user/info', {'sub': self.user['sub']})
        assert status_code == 200

        # test fake sub
        content, status_code = self.do_post('/user/info', {'sub': 'abcdFAKEnews'})
        assert status_code == 404

    @classmethod
    def do_post(self, endpoint, data):
        response = requests.post(f'{self.base_url}{endpoint}', json=data, headers=self.header)
        content, status_code = response.json(), response.status_code
        return content, status_code

