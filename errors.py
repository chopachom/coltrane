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
        self.key = kwargs.get('key')
        self.bucket = kwargs.get('bucket')



class InvalidAppIdException(StorageException):
    """Exception raised when application id is invalid"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class InvalidDocumentException(StorageException):
    """Exception raised when document is invalid"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class InvalidUserIdException(StorageException):
    """Exception raised when user id is invalid"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class InvalidDocumentIdException(StorageException):
    """Exception is raised when document id is invalid"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg