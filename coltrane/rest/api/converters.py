__author__ = 'Pasha'

from werkzeug.routing import BaseConverter
from werkzeug.exceptions import BadRequest
from coltrane.rest import exceptions
from coltrane.rest import validators

import json

class KeysConverter(BaseConverter):
    def to_python(self, value):
        keys = [k.strip() for k in value.split(',')]

        try:
            validators.KeyValidator(keys).validate()
        except exceptions.InvalidKeyNameError, e:
            raise InvalidKey(e.message)
        
        if not len(keys):
            raise InvalidKey('At least one key must be passed.')
        return keys

    def to_url(self, values):
        return ','.join(BaseConverter.to_url(value) for value in values)


class BucketConverter(BaseConverter):
    def __init__(self, url_map):
        super(BucketConverter, self).__init__(url_map)
        self.regex = r'[a-zA-Z0-9]+[a-zA-Z0-9\-_]*'


class SpecialBucketConverter(BaseConverter):
    def __init__(self, url_map):
        super(SpecialBucketConverter, self).__init__(url_map)
        self.regex = r'\.[a-zA-Z0-9\-_]+'


class InvalidKey(BadRequest):
    def __init__(self,description):
        super(InvalidKey, self).__init__(description)
        self.code = 400

    def get_body(self, environ):
        """Get the HTML body."""
        return json.dumps({'message':self.description})

    def get_headers(self, environ):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]
