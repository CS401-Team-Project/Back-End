"""
TODO: Module docstring
"""
from mongoengine import EmbeddedDocument, ObjectIdField, IntField, FloatField, BooleanField


class GroupSettings(EmbeddedDocument):
    """
    TODO: Class docstring
    """
    # can only the admin retrieve/view the join code
    only_admin_view_join_code = BooleanField(default=True)
    only_admin_set_join_code = BooleanField(default=True)
    only_admin_remove_user = BooleanField(default=True)
