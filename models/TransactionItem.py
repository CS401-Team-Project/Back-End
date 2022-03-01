from mongoengine import EmbeddedDocument, ObjectIdField, IntField, FloatField


class TransactionItem(EmbeddedDocument):
    # general info
    item_id = ObjectIdField(required=True)
    person = ObjectIdField(required=True)
    quantity = IntField(default=1, required=True)
    item_cost = FloatField(default=0.0, required=True)
