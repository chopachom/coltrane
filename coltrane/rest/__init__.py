from coltrane.rest.api.converters import KeysConverter, BucketConverter, SpecialBucketConverter

__author__ = 'apetrovich'

from coltrane.rest.api.v1 import api as api_v1

converters = {
    'keys': KeysConverter,
    'bucket': BucketConverter,
    'special': SpecialBucketConverter
}

__all__ = ['api_v1', 'converters']