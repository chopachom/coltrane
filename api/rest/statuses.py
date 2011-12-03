from coltrane import errors

__author__ = 'qweqwe'
from utils import Enum

STATUS_CODE = 'code'

class http(Enum):
    OK                    = 200
    BAD_REQUEST           = 400
    UNAUTHORIZED          = 401
    NOT_FOUND             = 404
    SERVER_ERROR          = 500
    NOT_IMPLEMENTED       = 501


class app(Enum):
    OK                = 0
    BAD_REQUEST       = 1
    APP_UNAUTHORIZED  = 2
    USER_UNAUTHORIZED = 3
    NOT_FOUND         = 4
    NOT_IMPLEMENTED   = 5
    SERVER_ERROR      = 6


ERROR_INFO_MATCHING = {
    errors.DocumentNotFoundError:   (app.NOT_FOUND, http.NOT_FOUND),
    errors.InvalidDocumentError:    (app.BAD_REQUEST, http.BAD_REQUEST),
    errors.InvalidDocumentKeyError: (app.BAD_REQUEST, http.BAD_REQUEST),
    errors.InvalidAppIdError:       (app.APP_UNAUTHORIZED, http.UNAUTHORIZED),
    errors.InvalidUserIdError:      (app.USER_UNAUTHORIZED, http.UNAUTHORIZED),
    errors.InvalidJSONFormatError:  (app.BAD_REQUEST, http.BAD_REQUEST),
    errors.InvalidRequestError:     (app.BAD_REQUEST, http.BAD_REQUEST)
}
