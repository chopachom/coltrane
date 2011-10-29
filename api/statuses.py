__author__ = 'qweqwe'
from utils import Enum

class http(Enum):
    OK              = 200
    BAD_REQUEST     = 400
    UNAUTHORIZED    = 401
    NOT_FOUND       = 404
    NOT_IMPLEMENTED = 501


class app(Enum):
    OK                = 0
    BAD_REQUEST       = 1
    APP_UNAUTHORIZED  = 2
    USER_UNAUTHORIZED = 3
    NOT_FOUND         = 4
    NOT_IMPLEMENTED   = 5
