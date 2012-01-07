# -*- coding: utf-8 -*-
import os
import shutil

__author__ = 'pshkitin'

import csv
from functools import wraps
import unittest
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

def save(doc):
    return storage.create(app_id, user_id, ip, doc, bucket)

def get(key):
    return storage.get(app_id, user_id, bucket, key)

def statistic(fn):
    @wraps(fn)
    def wrapper(self):
        res = fn(self)
        writer = csv.writer(open('statistic.csv', 'ab'), delimiter=',',
            quoting=csv.QUOTE_NONNUMERIC)
        friq = 1.0 / (self.duration / self.n)
        writer.writerow([fn.__doc__, self.n, self.duration, friq])
        print 'Doc number: %d; duration: %f seconds; friquency: %f' % \
              (self.n, self.duration, friq)
        return res
    return wrapper

class ApiBaseTestClass(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(ApiBaseTestClass, self).__init__(methodName=methodName)
        self.n = 0
        self.duration = 0

    @classmethod
    def setUpClass(cls):
        storage.entities.drop()
        try:
            os.remove('statistic.csv')
        except Exception:
            pass

    @classmethod
    def tearDownClass(cls):
        storage.entities.drop()

    @statistic
    def test_save1(self):
        """
            Сохранение маленького JSON документа много раз.
            Документ: doc = {'a': {'b':[1,2,3], 'c':'New Year'}}
        """
        self.n = 10000
        doc = {'a': {'b':[1,2,3], 'c':'New Year'}}
        start = time.time()
        for i in xrange(self.n):
            save(doc)
        duration = time.time() - start
        self.duration = duration

    @statistic
    def test_save2(self):
        """
            Сохранение среднего JSON документа много раз.
            Документ: doc = {'Key1dsfdsf': {'Key2sdfsdfsdf':[1,2,3], 'Key3dfgfdgfdg':'New Year'}}
        """
        self.n = 10000
        doc = {'Key1dsfdsf': {'Key2sdfsdfsdf':[1,2,3], 'Key3dfgfdgfdg':'New Year'}}
        start = time.time()
        for i in xrange(self.n):
            save(doc)
        duration = time.time() - start
        self.duration = duration


    @statistic
    def test_search1(self):
        """
            Поиск документа по ключу.
            Предварительно в БД записываются 10000 документов.
        """
        self.n = 1
        doc = {'Key1dsfdsf': {'Key2sdfsdfsdf':[1,2,3],
                              'Key3dfgfdgfdg':'New Year'}}

        for i in xrange(1000000):
            doc['_key'] = 'key_%d' % i
            save(doc)

        start = time.time()
        doc = get('key_999999')
        duration = time.time() - start
        self.duration = duration
        print 'Document found with key = ' + doc['_key']

if __name__ == '__main__':
    unittest.main()
