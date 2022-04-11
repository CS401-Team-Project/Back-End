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
        data = response.json()
        cond = (data['msg'] == "Smart Ledger API Endpoint: OK")
        if not cond:
            print('API is currently down')
            sys.exit()
        assert cond

    def test_register(self):
        """
        test
        :return:
        """
        content, status_code = self.do_post('/register', {})
        assert status_code == 200
        assert content['data']['sub'] == self.user['data']['sub']

    def test_delete_and_register(self):
        """
        test
        :return:
        """

        # delete
        content, status_code = self.do_post('/user/delete', {'sub': self.user['data']['sub']})
        assert status_code == 200
        assert content['msg'] == "User profile successfully deleted."

        # try to delete second time to ensure 404 is returned
        content, status_code = self.do_post('/user/delete', {'sub': self.user['data']['sub']})
        assert status_code == 404
        assert content['msg'] == "Token is unauthorized or user does not exist."

        # register new user for status_code 201
        content, status_code = self.do_post('/register', {})
        assert status_code == 201
        assert content['data']['sub'] == self.user['data']['sub']

        # try second register for status_code 200
        content, status_code = self.do_post('/register', {})
        assert content['data']['sub'] == self.user['data']['sub']
        assert status_code == 200

    def test_bad_payment(self):
        """
        test
        :return:
        """
        _, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200

        # assign preferred value as an option that hasn't been set
        data = {
            'pay_with': {
                'venmo': 'test venmo',
                'paypal': 'test paypal',
                'preferred': 'cashapp'
            }
        }
        content, status_code = self.do_post('/user/update', {'data': data})
        assert status_code == 200
        # TODO Change App.py to prevent a preferred payment method when the username hasn't been saved for that method

        # assign nonsense as 'pay_with' parameter
        data = {
            'pay_with': {
                'bad': 'data'
            }
        }
        content, status_code = self.do_post('/user/update', {'data': data})
        assert content['msg'] == "An unexpected error occurred."
        assert status_code == 500

    def test_user_info(self):
        """
        test
        :return:
        """
        # test legitimate sub
        _, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200

        # test fake sub
        _, status_code = self.do_post('/user/info', {'sub': 'baddatabaddatawhatchagonnado'})
        assert status_code == 404

        # test update pay with
        data = {
            'pay_with': {
                'venmo': 'test venmo',
                'cashapp': 'test cashapp',
                'paypal': 'test paypal',
                'preferred': 'venmo',
            }
        }
        content, status_code = self.do_post('/user/update', {'data': data})
        assert status_code == 200

        # check changes
        content, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200
        assert content['data']['pay_with'] == data['pay_with']

    def test_group_no_desc(self):
        """
        test
        :return:
        """

        # create a group
        data = {
            'name': 'test group name',
        }
        content, status_code = self.do_post('/group/create', {'data': data})
        self.group = content['data']
        assert status_code == 200

        # get the group
        content, status_code = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        assert status_code == 200
        assert content['data']['name'] == 'test group name'

        # delete the group
        content, status_code = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        assert status_code == 200

        # check persons groups
        content, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200
        assert self.group['_id'] not in content['data']['groups']

    def test_bad_group(self):
        """
        test
        :return:
        """

        # create a group with no data
        data = {
            'bad': 'data'
        }
        content, status_code = self.do_post('/group/create', {'data': data})
        assert content['msg'] == "Missing Required Field(s) / Invalid Type(s)."
        assert status_code == 400

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

        # check that admin is assigned correctly
        assert content['data']['admin'] == self.user['data']['sub']

        # get the group
        content, status_code = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        assert status_code == 200
        assert self.group == content['data']

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
        assert content['data']['name'] == 'test group update name'
        assert content['data']['desc'] == 'test group update description'

        # delete the group
        content, status_code = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        assert status_code == 200

        # check persons groups
        content, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        assert status_code == 200
        assert self.group['_id'] not in content['data']['groups']

    def test_invite(self):
        # create a group with list of invites
        invites = ['test1@email.com', 'test2@email.com', 'test3@email.com']
        data = {
            'name': 'test group name',
            'desc': 'test group description',
            'invites': invites
        }
        content, status_code = self.do_post('/group/create', {'data': data})
        assert status_code == 200
        self.group = content['data']

        # check invites
        content, status_code = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        assert status_code == 200
        assert invites == content['data']['invites']

        # delete the group
        content, status_code = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        assert status_code == 200

        # create new group with no invites
        invites = data.pop('invites')
        content, status_code = self.do_post('/group/create', {'data': data})
        assert status_code == 200
        self.group = content['data']
        assert len(self.group['invites']) == 0

        # invite via the invite api call
        content, status_code = self.do_post('/group/invite', {'id': self.group['_id']['$oid'], 'emails': invites})
        assert status_code == 200

        # check invites
        content, status_code = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        assert status_code == 200
        assert invites == content['data']['invites']

        # delete the group
        content, status_code = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        assert status_code == 200

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

    def test_join(self):
        # create a group with list of invites
        invites = ['test1@email.com', 'test2@email.com', self.user['data']['email']]
        data = {
            'name': 'test group name',
            'desc': 'test group description',
            'invites': invites
        }
        content, status_code = self.do_post('/group/create', {'data': data})
        assert status_code == 200
        self.group = content['data']

        content, status_code = self.do_post('/group/info', {'id': self.group['_id']['$oid']})
        assert status_code == 200
        assert self.group == content['data']

        # join group you created (you are already a member)
        content, status_code = self.do_post('/group/join', {'id': self.group['_id']['$oid']})
        assert status_code == 409
       

        # remove member that doesnt exist from group
        content, status_code = self.do_post('/group/remove-member', {'id': self.group['_id']['$oid'], 'userid': 'KonkyDong'})
        print(status_code)
        assert status_code == 409

        # delete the group
        content, status_code = self.do_post('/group/delete', {'id': self.group['_id']['$oid']})
        print(content)
        assert status_code == 200


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
    test.test_group_no_desc()
    test.test_bad_group()
    test.test_invite()
    test.teardown_class()
    test.test_delete_and_register()
    test.test_bad_payment()
