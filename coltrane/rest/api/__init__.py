__author__ = 'apetrovich'

from coltrane.rest.api.converters import KeyConverter
from .converters import KeysConverter, BucketConverter, SpecialBucketConverter
from .v1 import api as api_v1

converters = {
    'keys': KeysConverter,
    'key':  KeyConverter,
    'bucket': BucketConverter,
    'special': SpecialBucketConverter
}

__all__ = ['api_v1', 'converters']

