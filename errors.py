__author__ = 'qweqwe'

class StorageException(Exception):
    message = "Something gone wrong when dealing with storage"

    def __init__(self, *args, **kwargs):
        super(StorageException, self).__init__(*args)
        self.message = self.message.format(**kwargs)

    def __str__(self):
        return self.message


class EntryNotFoundError(StorageException):
    message = "Entry with key {key} was not found"

    def __init__(self, *args, **kwargs):
        super(EntryNotFoundError, self).__init__(*args, **kwargs)
        self.id = kwargs.get('key')
        self.bucket = kwargs.get('bucket')


class InvalidAppIdError(StorageException):
    """Error raised when application id is invalid"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class InvalidDocumentError(StorageException):
    """Error raised when document is invalid"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class InvalidUserIdError(StorageException):
    """Error raised when user id is invalid"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

    
class InvalidDocumentKeyError(StorageException):
    """Error is raised when document id is invalid"""
    message = "Invalid document key {key}"

    def __init__(self, *args, **kwargs):
        super(InvalidDocumentKeyError, self).__init__(*args, **kwargs)
        self.id = kwargs.get('key')
        self.bucket = kwargs.get('bucket')