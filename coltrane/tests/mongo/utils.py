# -*- coding: utf-8 -*-
import copy
from functools import wraps
import sys

__author__ = 'pshkitin'

import time
from pymongo.connection import Connection
from pymongo.database import Database
from coltrane.appstorage.storage import AppdataStorage

app_id = 'app_id'
user_id = 'user_id'
bucket = 'books'
ip = '127.0.0.1'

config = {
    'MONGODB_HOST':      '172.18.66.87',
    'MONGODB_PORT':       27017,
    'MONGODB_DATABASE':  'test_db',
    'MONGODB_SLAVE_OKAY': False,
    'MONGODB_USERNAME':   None,
    'MONGODB_PASSWORD':   None,
    'APPDATA_COLLECTION': 'appdata'
}

connection = Connection(
    host=config.get('MONGODB_HOST'),
    port=config.get('MONGODB_PORT'),
    slave_okay=config.get('MONGODB_SLAVE_OKAY')
)

database = Database(connection, config.get('MONGODB_DATABASE'))

db   = config['MONGODB_DATABASE']
coll = config['APPDATA_COLLECTION']
coll = connection[db][coll]

storage = AppdataStorage(coll)
storage.entities.drop()

def average(v):
    return sum(v, 0.0) / len(v)

def save(doc):
    return storage.create(app_id, user_id, ip, doc, bucket)

def get(key):
    return storage.get(app_id, user_id, bucket, key)

def find(filter):
        return storage.find(app_id, user_id, bucket, filter)

def update(filter, doc):
    storage.update(app_id, user_id, ip, bucket, doc, filter_opts=filter)

def duration_seconds(fn):
    @wraps(fn)
    def wrapper(*args):
        start = time.time()
        res = fn(*args)
        duration = time.time() - start
        return duration
    return wrapper

big_doc = {'a': {'b': [{'asdasdsadsad': {'sdafdsfdskfnbkjnb': [234324, 234324, 23234]}},
        {'asdasdsadsad': {'sdafdsfdskfnbkjnb': [234324, 234324, 23234]}},
        {'a': 234}],
                'Key3':
                        {'Key2': [{'asdasdsadsad': {'sdafdsfdskfnbkjnb': [234324, 234324, 23234]}},
                            {'asdasdsadsad': {'sdafdsfdskfnbkjnb': [234324, 234324, 23234]}},
                            {'a': 234}],
                         'Key3dfgfdgfdg': 'New Year'}}}

small_doc = {'a':{'b':10}, 'Key1': {'Key2': [1,2,3],
                      'Key3': 'abcdefjhi'}}

t = sys.argv[1]
if t == 'big':
    print 'Big document'
    document = big_doc
else:
    print 'Small document'
    document = small_doc
