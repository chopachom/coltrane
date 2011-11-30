__author__ = 'qweqwe'
    

class AppException(Exception):
    def __init__(self, message=None, *args, **kwargs):
        super(AppException, self).__init__(*args)
        if message:
            if  kwargs:
                self.message = message.format(**kwargs)
            else:
                self.message = message
        elif kwargs:
            if not self.message:
                raise RuntimeError("Formatting message before specifing the message itself")
            self.message = self.message.format(**kwargs)

    def __str__(self):
        return self.message


class DocumentNotFoundError(AppException):
    DOCUMENT_BY_CRITERIA = 'Document with bucket [{bucket}] and criteria [{criteria}] was not found'
    DOCUMENT_BY_KEY = 'Document with bucket [{bucket}] and key [{key}] was not found'

    message = DOCUMENT_BY_CRITERIA

    def __init__(self, message=None, **kwargs):
        super(DocumentNotFoundError, self).__init__(message, **kwargs)


class InvalidAppIdError(AppException):
    """Error raised when application is unauthorized or app id is invalid"""

    message = "App is unauthorized."

    def __init__(self, message=None, **kwargs):
        super(InvalidAppIdError, self).__init__(message, **kwargs)
        

class InvalidUserIdError(AppException):
    """Error raised when user is unauthorized or user id is invalid"""

    message = "User is unauthorized."
    
    def __init__(self, message=None, **kwargs):
        super(InvalidUserIdError, self).__init__(message, **kwargs)


class InvalidDocumentError(AppException):
    """Error raised when document is invalid"""
    FORBIDDEN_FIELDS_MSG = 'Document contains forbidden fields [%s]'
    
    def __init__(self, message, **kwargs):
        super(InvalidDocumentError, self).__init__(message, **kwargs)


class InvalidDocumentKeyError(AppException):
    """Error is raised when document id is invalid"""
    message = "No document with such key or invalid document key [{key}]"

    def __init__(self, message=None, *args, **kwargs):
        super(InvalidDocumentKeyError, self).__init__(message, *args, **kwargs)
        self.id = kwargs.get('key')
        self.bucket = kwargs.get('bucket')


class InvalidJSONFormatError(AppException):
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


class InvalidRequestError(AppException):
    message = "Invalid request syntax."

    def __init__(self, message=None, *args, **kwargs):
        super(InvalidRequestError, self).__init__(message, *args, **kwargs)
        self.req_url = kwargs.get('req_url')