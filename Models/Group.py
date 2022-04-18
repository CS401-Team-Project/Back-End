"""
EmbeddedDocuments for the Group model.
"""
import datetime
from mongoengine import *


class GroupPermissions(EmbeddedDocument):
    """
    EmbeddedDocument for the GroupPermissions model.
    """
    # only the admin can invite people
    only_admin_invite = BooleanField(default=True)

    # can only the admin modify transactions
    only_admin_remove_user = BooleanField(default=True)

    # can only the owner of a transaction modify it
    only_owner_modify_transaction = BooleanField(default=True)

    # can the admin overrule the owner of a transaction and modify it
    admin_overrule_modify_transaction = BooleanField(default=True)

    # can users delete transaction
    user_delete_transaction = BooleanField(default=True)

    # can only the owner of a transaction delete it
    only_owner_delete_transaction = BooleanField(default=True)

    # can the admin overrule the owner of a transaction and delete it
    admin_overrule_delete_transaction = BooleanField(default=True)


class GroupDate(EmbeddedDocument):
    """
    EmbeddedDocument for the GroupDate model.
    """
    created = DateTimeField(default=datetime.datetime.utcnow)
    updated = DateTimeField(default=datetime.datetime.utcnow)
    last_refreshed = DateTimeField(default=datetime.datetime.utcnow)


class GroupRestricted(EmbeddedDocument):
    """
    EmbeddedDocument for the GroupRestricted model.
    """
    permissions = EmbeddedDocumentField(GroupPermissions, default=GroupPermissions)
    balances = DictField(default={})
    ledger = DictField(default={})
    transactions = ListField(default=[])
    date = EmbeddedDocumentField(GroupDate, default=GroupDate)
    invite_list = ListField(default=[])

class Group(Document):
    """
    Document for the Group model.
    """
    name = StringField(max_length=60, required=True)
    desc = StringField(max_length=255, default='')
    admin = StringField(max_length=255, required=True)
    members = ListField(default=[])
    invites = ListField(default=[])
    restricted = EmbeddedDocumentField(GroupRestricted, default=GroupRestricted)

    # TODO: add time when person joined group ( embedded document or map )
    #   - date group was created
    #   - group settings
    #      - who can modify transactions (just creator or everyone, etc.)
