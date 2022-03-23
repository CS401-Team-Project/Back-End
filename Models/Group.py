"""
TODO: Module docstring
"""
from .GroupSettings import GroupSettings
from mongoengine import StringField, Document, ListField, EmbeddedDocumentField, DateField


class Group(Document):
    """
    TODO: Class Docstring
    """
    name = StringField(max_length=60, required=True)
    admin = StringField(max_length=255, required=True)
    join_code = StringField(max_length=255)
    people = ListField(default=[])
    transactions = ListField(default=[])
    settings = EmbeddedDocumentField(GroupSettings)

    # #
    # TODO - add time when person joined group ( embedded document or map )
    #   - date group was created
    #   - group settings
    #      - who can modify transactions (just creator or everyone, etc.)
