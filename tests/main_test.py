import requests
import sys
from dictdiffer import diff


class Tests:
    @classmethod
    def setup_class(self):
        """setup any state specific to the execution of the given class (which
        usually contains tests).
        """

        self.base_url = 'http://localhost:5000'
        # self.base_url = 'http://ddns.absolutzero.org:5555'

        with open('token.txt') as f:
            token = f.readline()
        self.header = {
            'Authorization': f'Bearer {token}'
        }

        # need to set up user stuff here for use later
        content, _ = self.do_post('/register', {})
        self.user = content

    @classmethod
    def teardown_class(self):
        """teardown any state that was previously setup with a call to
        setup_class.
        """
        pass

    def test_get(self):
        response = requests.get(self.base_url + '/test_get')
        cond = (response.content == b'Smart Ledger API Endpoint: OK')
        if not cond:
            print('API is currently down')
            sys.exit()
        assert cond

    def test_register(self):
        content, status_code = self.do_post('/register', {})
        assert status_code == 200

    def test_user_info(self):
        # test legitimate sub
        content, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200

        # test fake sub
        content, status_code = self.do_post('/user/info', {'sub': 'abcdFAKEnews'})
        assert status_code == 404

    def test_create_group(self):
        # create a group
        data = {
            'name': 'test group name',
            'desc': 'test group description'
        }
        content, status_code = self.do_post('/group/create', {'data': data})
        self.group = content['data']
        assert status_code == 200

        # get the group
        content, status_code = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        assert status_code == 200
        assert self.group == content

        # check persons groups
        content, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200
        user = content['data']
        assert self.group['_id'] in user['groups']

        # delete the group
        content, status_code = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        assert status_code == 200

        # check persons groups
        content, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200
        assert self.group['_id'] not in content['data']['groups']

    @classmethod
    def do_post(self, endpoint, data):
        response = requests.post(f'{self.base_url}{endpoint}', json=data, headers=self.header)
        content, status_code = response.json(), response.status_code
        return content, status_code


if __name__ == "__main__":
    test = Tests()
    test.setup_class()
    test.test_register()
    test.test_user_info()
    test.test_create_group()
    test.teardown_class()
