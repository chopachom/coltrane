# -*- coding: utf-8 -*-
__author__ = 'pshkitin'
from functools import wraps
import sys

import time
from pymongo.connection import Connection
from pymongo.database import Database
from coltrane.appstorage.storage import AppdataStorage, intf

index = False
app_id = 'app_id1'
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

def get_appid():
    return app_id


def average(v):
    return sum(v, 0.0) / len(v)

def save(doc):
    return storage.create(get_appid(), user_id, bucket, ip, doc)

def get(key):
    return storage.get(app_id, user_id, bucket, key)

def find(filter):
        return storage.find(app_id, user_id, bucket, filter)

def update(filter, doc):
    storage.update(app_id, user_id, bucket, ip, doc, filter_opts=filter)

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


def init_indexing():
    app_number = 100
    init_indexing.i = app_number
    app_ids = []
    for j in range(app_number):
        app_ids.append('app_id%d' % j)
    def get_appid_indexed():

        res = app_ids[init_indexing.i % app_number]
        init_indexing.i += 1
        return res
    global get_appid
    get_appid = get_appid_indexed

    coll.ensure_index(intf.HASHID)
#    coll.ensure_index('a.c.e')
#    coll.ensure_index([(intf.HASHID, 1), ('a.c.e', 1)])
    print 'With index: %s' % coll.index_information()


t = sys.argv[1]
if t == 'big':
    print 'Big document'
    document = big_doc
else:
    print 'Small document'
    document = small_doc

if len(sys.argv) > 2:
    if sys.argv[2] == 'index':
        init_indexing()
