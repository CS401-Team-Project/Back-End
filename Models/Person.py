"""
EmbeddedDocuments for the Person model.
"""
import datetime
from mongoengine import *


class PersonDate(EmbeddedDocument):
    """
    EmbeddedDocument storing dates related to a person.
    """
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)
    last_login = DateTimeField(default=datetime.datetime.utcnow)


class PayWith(EmbeddedDocument):
    """
    EmbeddedDocument storing the usernames for various payment methods.
    """
    venmo = StringField(default='')
    cashapp = StringField(default='')
    paypal = StringField(default='')
    preferred = StringField(default='')


class Person(Document):
    """
    Document storing a person's information.
    """
    sub = StringField(max_length=255, unique=True)
    first_name = StringField(max_length=60, required=True)
    last_name = StringField(max_length=60, required=True)
    email = EmailField(max_length=100, required=True)
    # TODO: can add email verified: https://developers.google.com/identity/sign-in/web/backend-auth
    email_verified = BooleanField(default=False, required=True)
    picture = StringField(max_length=255)
    groups = ListField(default=[])
    invites = ListField(default=[])
    date = EmbeddedDocumentField(PersonDate, default=PersonDate)
    pay_with = EmbeddedDocumentField(PayWith, default=PayWith)
