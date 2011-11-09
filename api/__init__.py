__author__ = 'apetrovich'

from api.converters import KeysConverter
from api.v1 import api as api_v1

converters = {}
converters['keys'] = KeysConverter

__all__ = ['api_v1', 'converters']