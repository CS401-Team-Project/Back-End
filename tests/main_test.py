import requests
import json
class UnitTests:
    def __init__(self):
        self.base_url = 'http://localhost:5000'
        with open('token.txt') as f:
            token = f.readline()
        self.header = {
            'Authorization': f'Bearer {token}'
        }

    def test_register(self):
        content, status_code = self.do_post('/register', {})
        self.user = content
        print(status_code)
        print(content)

    def test_user_info(self):
        content, status_code = self.do_post('/user/info', {'sub': self.user['data']['sub']})
        print(status_code)
        print(content)

    def do_post(self, endpoint, data):
        print(self.header)
        response = requests.post(f'{self.base_url}{endpoint}', json=data, headers=self.header)
        content, status_code = response.json(), response.status_code
        return content, status_code

if __name__ == "__main__":
    tests = UnitTests()
    tests.test_register()
    tests.test_user_info()

