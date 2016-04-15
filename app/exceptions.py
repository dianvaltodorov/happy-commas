from flask import jsonify


class InvalidUsage(Exception):
    """
    Invalid Usage exception thrown for bad usage.

    An exception class that can take a human readable message, a status code
    for the error and some optional payload to give more context for the error.
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
