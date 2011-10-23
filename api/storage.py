__author__ = 'qweqwe'

from ds import storage
from flask import request
from extensions.guard import guard

def get_user_id():
    return guard.current_user_token


def get_app_id():
    return guard.current_app_token

def get_remote_ip():
    request.get('remote_addr', None)


def save(bucket, document, key=None):
    if key is not None:
        document[storage.DOCUMENT_ID] = key
    return storage.create(get_app_id(), get_user_id(), get_remote_ip(),
                          document, bucket=bucket)

def get(bucket, key):
    return storage.read(get_app_id(), get_user_id(), key, bucket=bucket)


def update(bucket, document, key=None):
    return storage.update(get_app_id(), get_user_id(), get_remote_ip(),
                          document, bucket=bucket)

def delete(bucket, key):
    storage.delete(get_app_id(), get_user_id(), get_remote_ip(),
                          key, bucket=bucket)