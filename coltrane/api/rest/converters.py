from werkzeug.routing import BaseConverter

__author__ = 'Pasha'

class KeysConverter(BaseConverter):
    def to_python(self, value):
        keys = value.split(',')
        res_keys = []
        for k in keys:
            k = k.strip()
            if len(k):
                res_keys.append(k)

        return res_keys

    def to_url(self, values):
        return ','.join(BaseConverter.to_url(value)
        for value in values)


class BucketConverter(BaseConverter):
    def __init__(self, url_map):
        super(BucketConverter, self).__init__(url_map)
        self.regex = r'[a-zA-Z0-9]+[a-zA-Z0-9\-_]*'


class SpecialBucketConverter(BaseConverter):
    def __init__(self, url_map):
        super(SpecialBucketConverter, self).__init__(url_map)
        self.regex = r'\.[a-zA-Z0-9\-_]+'