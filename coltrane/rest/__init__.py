from pymongo.errors import OperationFailure
from coltrane.rest import exceptions
from coltrane.utils import Enum

__author__ = 'apetrovich'


STATUS_CODE = 'code'

class http_status(Enum):

    OK                    = 200
    CREATED               = 201

    BAD_REQUEST           = 400
    UNAUTHORIZED          = 401
    NOT_FOUND             = 404
    CONFLICT              = 409

    SERVER_ERROR          = 500
    NOT_IMPLEMENTED       = 501


class app_status(Enum):
    OK                = 0
    BAD_REQUEST       = 1
    CREATED           = 2
    NOT_FOUND         = 3
    CONFLICT          = 4
    APP_UNAUTHORIZED  = 5
    USER_UNAUTHORIZED = 6
    NOT_IMPLEMENTED   = 7
    SERVER_ERROR      = 8



ERROR_INFO_MATCHING = {
    exceptions.InvalidKeyNameError:        (app_status.BAD_REQUEST, http_status.BAD_REQUEST),
    exceptions.DocumentAlreadyExistsError: (app_status.CONFLICT, http_status.CONFLICT),
    exceptions.InvalidDocumentFieldsError:    (app_status.BAD_REQUEST, http_status.BAD_REQUEST),
    exceptions.InvalidJSONFormatError:  (app_status.BAD_REQUEST, http_status.BAD_REQUEST),
    exceptions.InvalidRequestError:     (app_status.BAD_REQUEST, http_status.BAD_REQUEST),
    OperationFailure: (app_status.BAD_REQUEST, http_status.BAD_REQUEST)
}