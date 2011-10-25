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

class EntryNotFoundError(AppException):
    message = 'Document with bucket {bucket} and key {key} is not found'

    def __init__(self, *args, **kwargs):
        super(EntryNotFoundError, self).__init__(*args, **kwargs)
        self.id = kwargs.get('key')
        self.bucket = kwargs.get('bucket')


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
    def __init__(self, message, **kwargs):
        super(InvalidDocumentError, self).__init__(message, **kwargs)


class InvalidDocumentKeyError(AppException):
    """Error is raised when document id is invalid"""
    message = "Invalid document key {key}"

    def __init__(self, message=None, *args, **kwargs):
        super(InvalidDocumentKeyError, self).__init__(message, *args, **kwargs)
        self.id = kwargs.get('key', None)
        self.bucket = kwargs.get('bucket', None)