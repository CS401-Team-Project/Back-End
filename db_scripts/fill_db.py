# general utils
import json
import os
import sys
import string

# for the randomness
import random
import names
import randomname
import numpy as np

# flask imports
from flask import Flask
from flask_mongoengine import MongoEngine

# add the models package to the path
import path
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)
from models import *

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': os.environ['MONGODB_HOST'],
    'username': os.environ['MONGODB_USERNAME'],
    'password': os.environ['MONGODB_PASSWORD'],
    'authSource': 'smart-ledger',
    'db': 'smart-ledger',

}

db = MongoEngine()
db.init_app(app)


# get config for data generation
config = 'db_scripts/example_data/data_gen_config.json'
if len(sys.argv) == 2:
    config = sys.argv[1]
with open(config, 'r') as f:
    config = json.load(f)

# read config variables
seed = int(config['seed'])
email_domains = config['email_domains']
min_email_len, max_email_len = int(config['min_email_len']), int(config['max_email_len'])
num_users = int(config['num_users'])
num_groups = int(config['num_groups'])
min_group_size, max_group_size = int(config['min_group_size']), int(config['max_group_size'])
min_transactions, max_transactions = int(config['min_transactions']), int(config['max_transactions'])
min_item_quantity, max_item_quantity = int(config['min_transactions']), int(config['max_item_quantity'])
min_item_per_transac_item, max_item_per_transac_item = int(config['min_item_per_transac_item']), int(config['max_item_per_transac_item'])
min_item_price, max_item_price = float(config['min_item_price']), float(config['max_item_price'])
email_usernames = config['email_usernames'] if 'email_usernames' in config else None
name_list = config['names'] if 'names' in config else None

# get list of domain names for email generation
with open(email_domains, 'r') as f:
    email_domains = json.load(f)

if email_usernames is not None:
    with open(email_usernames, 'r') as f:
        email_usernames = json.load(f)

if name_list is not None:
    with open(name_list, 'r') as f:
        name_list = json.load(f)

# fix some values if needed
dec_if_equal = lambda x, y, dec=1: x-dec if x == y else x
min_group_size = dec_if_equal(min_group_size, max_group_size)
min_group_size = dec_if_equal(min_group_size, max_group_size)
min_email_len = dec_if_equal(min_email_len, max_email_len)
min_transactions = dec_if_equal(min_transactions, max_transactions)
min_item_quantity = dec_if_equal(min_item_quantity, max_item_quantity)
min_item_per_transac_item = dec_if_equal(min_item_per_transac_item, max_item_per_transac_item)
min_item_price = dec_if_equal(min_item_price, max_item_price, 0.1)

# some error checking for my sanity
if email_usernames is not None:
    assert len(email_usernames) >= num_users
if name_list is not None:
    assert len(name_list) >= num_users

assert num_users >= 1
assert num_groups >= 1
assert max_group_size > min_group_size >= 1
assert max_email_len > min_email_len >= 1
assert max_transactions > min_transactions >= 1
assert max_item_quantity > min_item_quantity >= 1
assert max_item_per_transac_item > min_item_per_transac_item >= 1
assert max_item_price > min_item_price > 0

# seed the randomness
np.random.seed(seed)
random.seed(seed)


def random_char(char_num):
    return ''.join(random.choice(string.ascii_letters) for _ in range(char_num))


def get_one_random_domain(domains):
    return random.choice(domains)


# add people to database
p_ids = []
for i in range(num_users):
    first_name, last_name = (names.get_first_name(), names.get_last_name()) if name_list is None else (name_list[i]['first_name'], name_list[i]['last_name'])
    username = f'{first_name}_{last_name}_{np.random.randint(0,1000):0>4}' if email_usernames is None else email_usernames[i]
    p = {
        "first_name": first_name,
        "last_name": last_name,
        "email": f"{username}@{get_one_random_domain(email_domains)}"
    }
    p = Person(**p)
    p.save()
    p_ids.append(p.id)

# add groups to database
g_ids = []
for group in range(num_groups):
    g = {
        'name': randomname.generate('a/appearance', 'a/size', 'n/dogs').replace('-', ' ')
    }
    g = Group(**g)
    g.save()
    g_ids.append(g.id)

# randomly link people to groups
people = Person.objects()
groups = Group.objects()
num_groups = len(people)
num_people = len(groups)
people_indices = np.arange(0,num_people)
group_people = {}
for g in groups:
    people_to_add = np.random.choice(people_indices, np.random.randint(min_group_size, max_group_size))
    group_people[g.id] = []
    for i, p in enumerate(people):
        if i in people_to_add:
            p.groups.append(g.id)
            p.save()
            g.people.append(p.id)
            g.save()
            group_people[g.id].append(p.id)

# randomly add transactions to group
t_ids = []
transaction_group = {}
for g_id in g_ids:
    num_p_g = len(group_people[g_id])
    # generate # transactions specified in config
    for i in range(np.random.randint(min_transactions, max_transactions)):
        # create some random transaction and save its id for later
        p_id_i = np.random.randint(0, num_p_g)
        t = {
            'title': randomname.generate('ipsum/hipster', 'n/food').replace('-', ' '),
            'desc': randomname.generate('v/cooking', 'a/taste', 'n/food').replace('-', ' '),
            'group': g_id,
            'created_by': group_people[g_id][p_id_i],
            'modified_by': group_people[g_id][p_id_i],
            'vendor': randomname.generate('a/taste', 'n/shopping', 'n/buildings').replace('-', ' ')
        }

        t = Transaction(**t)
        t.save()
        transaction_group[t.id] = g_id
        t_ids.append(t.id)


# randomly add items to transactions
def random_float(low, high):
    return np.random.random()*(high-low) + low


# add random number of items into a transaction
for t_id in t_ids:
    t = Transaction.objects(id=t_id).first()
    g_id = transaction_group[t_id]
    num_p_g = len(group_people[g_id])
    total_price = 0
    for _ in range(np.random.randint(min_item_per_transac_item, max_item_per_transac_item)):
        item_cost = random_float(min_item_price, max_item_price)
        quantity = np.random.randint(min_item_quantity, max_item_quantity)

        item_d = {
            'name': randomname.generate('v/cooking', 'n/fast_food').replace('-', ' '),
            'desc': randomname.generate('ipsum/hipster', 'n/condiments', 'n/meat').replace('-', ' '),
            'unit_price': item_cost
        }
        # TODO if the item has been randomly generated and it matches another one (extremely small chance)
        #   don't create a new one. rather use the same document and increment its usage_count
        item = Item.objects(**item_d).first()
        if item is None:
            item = Item(**item_d)
        else:
            item.usage_count += 1
        item.save()

        i_id = item.id
        p_id_i = np.random.randint(0, num_p_g)

        transac_item = {
            'item_id': i_id,
            'person': group_people[g_id][p_id_i],
            'quantity': quantity,
            'item_cost': item_cost*quantity
        }
        transac_item = TransactionItem(**transac_item)
        total_price += item_cost*quantity
        t.items.append(transac_item)
        t.save()
    t.total_price = total_price
    t.save()

