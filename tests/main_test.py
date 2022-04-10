import requests
import sys


class Tests:
    """
    tests
    """
    @classmethod
    def setup_class(cls):
        """setup any state specific to the execution of the given class (which
        usually contains tests).
        """

        cls.base_url = 'http://localhost:5000'
        # self.base_url = 'http://ddns.absolutzero.org:5555'

        with open('token.txt') as file:
            token = file.readline()
        cls.header = {
            'Authorization': f'Bearer {token}'
        }

        # need to set up user stuff here for use later
        content, _ = cls.do_post('/register', {})
        cls.user = content
        cls.group = None

    @classmethod
    def teardown_class(cls):
        """teardown any state that was previously setup with a call to
        setup_class.
        """
        pass

    def test_get(self):
        """
        test
        :return:
        """
        response = requests.get(self.base_url + '/test_get')
        cond = (response.content == b'Smart Ledger API Endpoint: OK')
        if not cond:
            print('API is currently down')
            sys.exit()
        assert cond

    def test_register(self):
        """
        test
        :return:
        """
        _, status_code = self.do_post('/register', {})
        assert status_code == 200

    def test_user_info(self):
        """
        test
        :return:
        """
        # test legitimate sub
        _, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200

        # test fake sub
        _, status_code = self.do_post('/user/info', {'sub': 'abcdFAKEnews'})
        assert status_code == 404

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

        # update normal group stuff
        data = {
            'name': 'test group update name',
            'desc': 'test group update description'
        }
        content, status_code = self.do_post('/group/update', {'id': self.group['_id']['$oid'], 'data': data})
        assert status_code == 200

        # get the group
        content, status_code = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        assert status_code == 200
        assert content['name'] == 'test group update name'
        assert content['desc'] == 'test group update description'

        # delete the group
        content, status_code = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        assert status_code == 200

        # check persons groups
        content, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200
        assert self.group['_id'] not in content['data']['groups']

    @classmethod
    def do_post(cls, endpoint, data):
        """
        test
        :return:
        """
        response = requests.post(f'{cls.base_url}{endpoint}', json=data, headers=cls.header)
        content, status_code = response.json(), response.status_code
        return content, status_code


if __name__ == "__main__":
    test = Tests()
    test.setup_class()
    test.test_register()
    test.test_user_info()
    test.test_create_group()
    test.teardown_class()
