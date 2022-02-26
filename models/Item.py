from mongoengine import *


class Item(Document):
    # general info
    name            = StringField(default='', max_length=60, required=True)
    desc            = StringField(default='', required=True)
    unit_price      = FloatField(default=0.0, required=True)

    # generate the id based off a hash of its main values
    # hash             = ObjectIdField(default=str(hash(f'{name}-{desc}-{unit_price}')), primary_key=True)

    # if the usage_count turns to 0 we delete it from the db
    usage_count     = IntField(default=1)

    # TODO - automatic total price calculation
    #     - Where and what object need restrictions