__author__ = 'qweqwe'

from coltrane.exceptions import AppException

class ApiError(AppException):
    pass


class InvalidJSONFormatError(ApiError):
    """
    Error when user passes invalid json object
    Parameters:
    message: String. Have to have special format if json would be passed too.
        Format sample: "Error while format JSON obj. JSON obj= {json}"
    json=<json_obj>: should be passed with a key=value format
    """

    message = "Invalid json object."

    def __init__(self, message=None, *args, **kwargs):
        super(InvalidJSONFormatError, self).__init__(message, *args, **kwargs)
        self.json = kwargs.get('json')


class InvalidRequestError(ApiError):
    message = "Invalid request syntax."

    def __init__(self, message=None, *args, **kwargs):
        super(InvalidRequestError, self).__init__(message, *args, **kwargs)
        self.req_url = kwargs.get('req_url')


class InvalidDocumentFieldsError(ApiError):
    """Error raised when document is invalid"""
    FORBIDDEN_FIELDS_MSG = 'Document contains forbidden fields [%s]'

    def __init__(self, message, **kwargs):
        super(InvalidDocumentFieldsError, self).__init__(message, **kwargs)