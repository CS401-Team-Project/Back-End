### [<= Back to `README.md`](../README.md)
## Running Unit Tests
### **You will have to redo this process multiple times since auth tokens expire after a brief period of time.**
### Create `token.txt` in `~/Smart-Ledger/Back-End/tests/`
```shell
touch tests/token.txt
```

### Make Sure Git Repos are up to Date:
```shell
cd ~/Smart-Ledger/
git checkout main
git pull origin main

cd ./Front-End/
git checkout main
git pull origin main

cd ../Back-End/
git checkout main
git pull origin main
```

### Start Full Application Stack:
```shell
cd ~/Smart-Ledger/
docker-compose up -d --build
```
### Login and Retrieve Token:
- Go to `localhost:3000` and log in with your Google account
- Click 'API Client' under 'Other' on the left-hand side. (Click the hamburger in the top left if you don't see this option)
- Copy the Auth Token and paste in `token.txt`

### Run Tests in New Shell
```shell
cd tests
pytest main_test.py -v
```