"""
TODO: Module Docstring
"""
from mongoengine import StringField, Document, FloatField, IntField


class Item(Document):
    """
    TODO: Class Docstring
    """
    # general info
    name = StringField(default='', max_length=60, required=True)
    desc = StringField(default='', required=True)
    unit_price = FloatField(default=0.0, required=True)

    # if the usage_count turns to 0 we delete it from the db
    usage_count = IntField(default=0)

    # TODO - automatic total price calculation
    #     - Where and what object need restrictions
