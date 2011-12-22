from time import sleep
from pymongo.cursor import Cursor
from pymongo.errors import AutoReconnect
from coltrane.appstorage.exceptions import StorageError

__author__ = 'qweqwe'


AUTO_RECONNECT_ATTEMPTS = 10
AUTO_RECONNECT_DELAY = 0.1

def auto_reconnect(func):
    """
    Function wrapper to automatically reconnect if AutoReconnect is raised.

    If still failing after AUTO_RECONNECT_ATTEMPTS, raise the exception after
    all. Technically this should be handled everytime a mongo query is
    executed so you can gracefully handle the failure appropriately, but this
    intermediary should handle 99% of cases and avoid having to put
    reconnection code all over the place.

    """
    def retry_function(*args, **kwargs):
        attempts = 0
        while True:
            try:
                return func(*args, **kwargs)
            except AutoReconnect, e:
                attempts += 1
                if attempts > AUTO_RECONNECT_ATTEMPTS:
                    raise StorageError('%s raised [%s] -- AutoReconnecting (#%d)...\n' % (
                        func.__name__, e, attempts))
                sleep(AUTO_RECONNECT_DELAY)
    return retry_function

# monkeypatch: wrap Cursor.__send_message (name-mangled)
Cursor._Cursor__send_message = auto_reconnect(Cursor._Cursor__send_message)