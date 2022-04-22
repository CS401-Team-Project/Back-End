from start_test import *


class GroupTests(Tests):
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
        assert self.group == response.json()['data']

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
        response = self.do_post('/group/update', {'id': self.group['_id']['$oid'], 'data': data})
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