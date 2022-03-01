from mongoengine import StringField, Document, ListField


class Group(Document):
    name = StringField(max_length=60, required=True)
    people = ListField(default=[])
    transactions = ListField(default=[])
    # TODO - add time when person joined group ( embedded document or map )
    #   - date group was created
    #   - owner of group
    #   - group settings
    #      - who can modify transactions (just creator or everyone, etc.)
