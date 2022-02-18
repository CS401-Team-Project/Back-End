# Back-End


## to set up db 
1. docker exec -it mongo bash
2. mongo -u admin -p
3. use smart_ledger
4. db.createUser({user: 'apiuser', pwd: 'apipassword', roles: [{role: 'readWrite', db: 'smart_ledger'}]})

TODO - make script to do this automatically