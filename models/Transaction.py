from mongoengine import *
from .TransactionItem import TransactionItem
import datetime

class Transaction(Document):
    # general info
    title           = StringField(max_length=60, required=True)
    desc            = StringField(default='', required=False)

    # linking
    group           = ObjectIdField(required=True)

    # keep track of when and who created it
    date_created    = DateTimeField(default=datetime.datetime.utcnow)
    created_by      = ObjectIdField(required=True)

    # keep track of when and who last modified it
    date_modified   = DateTimeField(default=datetime.datetime.utcnow)
    modified_by     = ObjectIdField(required=True)

    # required meta data
    total_price     = FloatField(default=0.0)
    items           = EmbeddedDocumentListField(document_type=TransactionItem)

    # optional meta data
    vendor          = StringField(default='', required=False)
    # TODO - have this as its own collection and have it hold the id to the receipt document
    # receipt         = ImageField(required=False)
