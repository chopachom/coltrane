__author__ = 'qweqwe'

from coltrane.exceptions import AppException


class StorageError(AppException):
    pass



class DocumentNotFoundError(StorageError):
    DOCUMENT_BY_CRITERIA = 'Document with bucket [{bucket}] and criteria [{criteria}] was not found'
    DOCUMENT_BY_KEY = 'Document with bucket [{bucket}] and key [{key}] was not found'

    message = DOCUMENT_BY_CRITERIA

    def __init__(self, message=None, **kwargs):
        super(DocumentNotFoundError, self).__init__(message, **kwargs)



class InvalidAppIdError(StorageError):
    """Error raised when application id is invalid"""

    message = "Invalid app_id [{app_id}]"

    def __init__(self, message=None, **kwargs):
        super(InvalidAppIdError, self).__init__(message, **kwargs)



class InvalidUserIdError(StorageError):
    """Error raised when user id is invalid"""

    message = "Invalid user id [{user_id}]"

    def __init__(self, message=None, **kwargs):
        super(InvalidUserIdError, self).__init__(message, **kwargs)



class InvalidDocumentKeyError(StorageError):
    """Error raised when user id is invalid"""

    message = "Invalid document key [{key}]"

    def __init__(self, message=None, **kwargs):
        super(InvalidDocumentKeyError, self).__init__(message, **kwargs)



class InvalidDocumentError(StorageError):
    """Error raised when document is invalid"""
    message = 'Invalid document'

    def __init__(self, message, **kwargs):
        super(InvalidDocumentError, self).__init__(message, **kwargs)



class DocumentAlreadyExistsError(StorageError):
    """Error is raised when document id is invalid"""
    message = "No document with such key or invalid document key [{key}]"

    def __init__(self, message=None, *args, **kwargs):
        super(DocumentAlreadyExistsError, self).__init__(message, *args, **kwargs)
        self.id = kwargs.get('key')
        self.bucket = kwargs.get('bucket')