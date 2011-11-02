from werkzeug.routing import BaseConverter

__author__ = 'Pasha'

class KeysConverter(BaseConverter):
    def to_python(self, value):
        keys = value.split(',')
        keys = map(lambda k: k.strip(), keys)

        if len(keys) == 0:
            raise RuntimeError('At least one key must be passed.')
        return keys

    def to_url(self, values):
        return ','.join(BaseConverter.to_url(value)
        for value in values)