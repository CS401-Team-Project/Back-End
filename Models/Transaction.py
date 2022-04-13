"""
EmbeddedDocuments for Transaction
"""
import datetime

from mongoengine import *


class Item(Document):
    """
    Item class
    """
    # general info
    name = StringField(default='', max_length=60, required=True)
    desc = StringField(default='', required=True)
    unit_price = FloatField(default=0.0, required=True)

    # if the usage_count turns to 0 we delete it from the db
    usage_count = IntField(default=0)


class TransactionItem(EmbeddedDocument):
    """
    TransactionItem class
    """
    # general info
    item_id = ObjectIdField(required=True)
    person = ObjectIdField(required=True)
    quantity = IntField(default=1, required=True)
    item_cost = FloatField(default=0.0, required=True)
    # TODO: last modified and modified by


class Transaction(Document):
    """
    Transaction class
    """
    # general info
    title = StringField(max_length=60, required=True)
    desc = StringField(default='', required=False)

    # linking
    group = ObjectIdField(required=True)

    #
    date_purchased = DateTimeField(default=datetime.datetime.utcnow)

    # keep track of when and who created it
    date_created = DateTimeField(default=datetime.datetime.utcnow)
    created_by = ObjectIdField(required=True)

    # keep track of when and who last modified it
    date_modified = DateTimeField(default=datetime.datetime.utcnow)
    modified_by = ObjectIdField(required=True)

    # required meta data
    total_price = FloatField(default=0.0)
    items = EmbeddedDocumentListField(document_type=TransactionItem)

    # optional meta data
    vendor = StringField(default='', required=False)
    # TODO: have this as its own collection and have it hold the id to the receipt document
    # receipt         = ImageField(required=False)
