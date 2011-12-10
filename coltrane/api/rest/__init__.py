__author__ = 'apetrovich'

from .converters import KeysConverter, BucketConverter, SpecialBucketConverter
from .v1 import api as api_v1

converters = {
    'keys': KeysConverter,
    'bucket': BucketConverter,
    'special': SpecialBucketConverter
}

__all__ = ['api_v1', 'converters']