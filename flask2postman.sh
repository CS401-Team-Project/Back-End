#!/bin/bash

flask2postman App.create_app --name "Smart Ledger API" --base_url 127.0.0.1:5000 -i > postman_api.json
