from start_test import *


class UserTests(Tests):
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

