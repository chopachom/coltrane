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

