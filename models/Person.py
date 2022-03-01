import datetime

from mongoengine import StringField, Document, EmailField, ListField, DateTimeField


class Person(Document):
    first_name = StringField(max_length=60, required=True)
    last_name = StringField(max_length=60, required=True)
    email = EmailField(max_length=100, required=True)
    groups = ListField(default=[])
    date_joined = DateTimeField(default=datetime.datetime.utcnow)
    # TODO - Fields to add
    #  - API Key ( will have to change regularly )
    #  - API Key Last Generated ( for google auth and email auth )
    #  - Password ( hash plus salted - only for email auth )
    #  - sub object ( Embedded Document )
    #      - CashApp, Venmo, and user names
