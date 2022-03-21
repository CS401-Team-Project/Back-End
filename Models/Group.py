"""
TODO: Module docstring
"""
from . import GroupSettings
from mongoengine import StringField, Document, ListField, EmbeddedDocument


class Group(Document):
    """
    TODO: Class Docstring
    """
    name = StringField(max_length=60, required=True)
    admin = StringField(max_length=255, required=True)
    join_code = StringField(max_length=255)
    people = ListField(default=[])
    transactions = ListField(default=[])
    settings = EmbeddedDocument(GroupSettings)
    # TODO - add time when person joined group ( embedded document or map )
    #   - date group was created
    #   - owner of group
    #   - group settings
    #      - who can modify transactions (just creator or everyone, etc.)
