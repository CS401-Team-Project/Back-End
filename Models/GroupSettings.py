"""
TODO: Module docstring
"""
from mongoengine import EmbeddedDocument, BooleanField


class GroupSettings(EmbeddedDocument):
    """
    TODO: Class docstring
    """
    # can only the admin retrieve/view the join code
    only_admin_view_join_code = BooleanField(default=True)
    only_admin_set_join_code = BooleanField(default=True)

    # can only the admin modify transactions
    only_admin_remove_user = BooleanField(default=True)

    # can only the owner of a transaction modify it
    only_owner_modify_transaction = BooleanField(default=True)

    # can the admin overrule the owner of a transaction and modify it
    admin_overrule_transaction = BooleanField(default=True)
