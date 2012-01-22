# -*- coding: utf-8 -*-
"""
    :Authors: - pshkitin
"""

import datetime
import re

from time import sleep
from pymongo.cursor import Cursor
from pymongo.errors import AutoReconnect
from coltrane.appstorage.exceptions import StorageError
from coltrane.utils import Enum


AUTO_RECONNECT_ATTEMPTS = 10
AUTO_RECONNECT_DELAY = 0.1

DOCUMENT_ID_FORMAT = '{app_id}|{user_id}|{bucket}|{deleted}|{document_key}'

class reservedf(Enum):
    BUCKET      = '_bucket'
    CREATED_AT  = '_created_at'
    UPDATED_AT  = '_updated_at'

class intf(Enum):
    ID          = '_id'
    APP_ID      = '__app_id__'
    USER_ID     = '__user_id__'
    HASHID      = '__hashid__'
    DELETED     = '__deleted__'
    IP_ADDRESS  = '__ip_address__'

class extf(Enum):
    KEY         = '_key'

# Atomic operations for mongodb and their service fields such as $gt for $pullAll
atomic_operations = ['$set', '$unset', '$inc',
                     '$push', '$pushAll', '$pop',
                     '$pull', '$pullAll', '$addToSet', '$each']

service_fields_for_atomic = ['$gt', '$gte', '$lt', '$lte', '$ne', '$in', '$nin', '$mod']


class forbidden_fields(Enum):
    WHERE      = '$where'
    EXISTS     = '$exists'
    TYPE       = '$type'
    ID         = intf.ID


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


def _internal_id(app_id, user_id, bucket, deleted, document_key):
    return DOCUMENT_ID_FORMAT.format(app_id=app_id, user_id=user_id,
        bucket=bucket, deleted=deleted,
        document_key=document_key)

def _external_key(internal_id):
    """
        Returns external _key by given internal id
        example: applolo|usrlolo|ololo|flafffnl|asdf|asd| -> flaflaffnl|asdf|asd|
    """
    return '|'.join(substr for substr in internal_id.split('|')[4:])


reg = re.compile(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d*))?Z?$')
def try_convert_to_date(data):
    res = re.match(reg, data)
    if res:
        val = [int(x) if x else 0 for x in res.groups()]
        return datetime.datetime(*val)
    else:
        return data
