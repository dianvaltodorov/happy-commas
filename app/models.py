from app import db


class Entry(db.Model):
    """Representation of a entry. Contain user id, key and value"""
    __tablename__ = 'entries'
    user_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(128), primary_key=True)
    value = db.Column(db.Text(), nullable=False)

    def __init__(self, user_id, key, value):
        self.user_id = user_id
        self.key = key
        self.value = value

    def csv_repr(self):
        """
        Return a list representation of an entry suitable for saving in a csv.
        """
        return [self.user_id, self.key, self.value]

    def __repr__(self):
        representation = '<Entry user_id: {0}, key: {1}, value: {2}>'
        return representation.format(self.user_id, self.key, self.value)
