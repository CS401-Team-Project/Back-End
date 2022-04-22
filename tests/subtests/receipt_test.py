from start_test import *

global TRANSACTION_ID
global RECEIPT_STRING


class ReceiptTests(Tests):

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
        assert self.group == response.json()['data']

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
        self.TRANSACTION_ID = response.json()['id']

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
        with open('images/test_image_1.png', 'wb') as bin_file:
            bin_file.write(receiptBytes)

        file_like = base64.b64decode(RECEIPT_STRING)
        receiptBytes = bytearray(file_like)
        with open('images/test_image_2.png', 'wb') as bin_file:
            bin_file.write(receiptBytes)