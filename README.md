# Back-End

[![Pylint](https://github.com/CS401-Team-Project/Back-End/actions/workflows/pylint.yml/badge.svg)](https://github.com/CS401-Team-Project/Back-End/actions/workflows/pylint.yml)

## Peaking at the mongo db
1. docker exec -it mongo bash
2. mongo -u admin -p 
3. mongo -u apiuser -p apipassword --authenticationDatabase smart-ledger
4. use smart-ledger

# TODO: Create separate README section for writing and running Unit Tests
## Running tests
### Create `token.txt` in `~/Smart-Ledger/Back-End/tests/`
```shell
touch tests/token.txt
```


#### In `Smart-Ledger/Front-End/.env.development`, change endpoint:
```shell
//.env.development
REACT_APP_API_ENDPOINT=http://ddns.absolutzero.org:5555/
```

#### Start Front-End:
```shell
cd ../Front-End
npm install (only required on first run)
npm install react-scripts -g (only required on first run)
npm start
```
### Login and Retrieve Token:
Click 'API Client' under 'Other' on the left-hand side.
Copy the Auth Token and paste in `token.txt`

### Spin Back-End Up
npm can be exited. Go back to `Smart-Ledger` and run `docker-compose up --build api`. 
This will take a few seconds.
```shell
cd ~/Smart-Ledger/
docker-compose up --build api
```

### Run Tests in New Shell
```shell
cd tests
pytest main_test.py -v
```


