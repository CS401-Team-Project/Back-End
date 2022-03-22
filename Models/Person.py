"""
TODO: Module docstring
"""
import datetime

from mongoengine import StringField, Document, EmailField, ListField, DateTimeField, ObjectIdField


class Person(Document):
    """
    TODO: Class docstring
    """
    first_name = StringField(max_length=60, required=True)
    last_name = StringField(max_length=60, required=True)
    email = EmailField(max_length=100, required=True)
    groups = ListField(default=[])
    date_joined = DateTimeField(default=datetime.datetime.utcnow)
    picture = StringField(max_length=255)
    sub = StringField(max_length=255, unique=True)

    # TODO - Fields to add
    #  - can add email verified: https://developers.google.com/identity/sign-in/web/backend-auth
    #  - sub object ( Embedded Document )
    #      - CashApp, Venmo, and user names
