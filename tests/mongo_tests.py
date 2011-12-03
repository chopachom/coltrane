import unittest
from pymongo.connection import Connection

from coltrane.api import config
from coltrane.appstorage.storage import AppdataStorage
from coltrane.appstorage.storage import extf


test_database   = config.TestConfig.MONGODB_DATABASE
test_collection = config.TestConfig.APPDATA_COLLECTION
c = Connection()
storage = AppdataStorage(c[test_database][test_collection])


__author__ = 'Pasha'

ip = '127.0.0.1'
app_id = '1'
user_id = '1'
bucket = 'books'

class SecurityTestCase(unittest.TestCase):
    def setUp(self):
        for i in range(10):
            data = {'a': i, 'b': [1, 2, 3, i]}
            storage.create(app_id, user_id, ip, data, bucket=bucket)


    def tearDown(self):
        storage.entities.drop()

    def test_security_when_where_used(self):
        filter_opts = {'a': {'$gt': 5}, '$where': 'db.entities.drop()'}

        with self.assertRaises(Exception):
            storage.find(app_id, user_id, bucket, filter_opts)

        res = storage.find(app_id, user_id, bucket)
        assert 10 == len(res)

        filter_opts = {'$where': 'db.dropDatabase()'}
        storage.find(app_id, user_id, bucket, filter_opts)

        res = storage.find(app_id, user_id, bucket)
        assert 10 == len(res)

        with self.assertRaises(Exception):
            storage.find(app_id, user_id, bucket, {"$where": "db.entities.drop()"})
        res = storage.find(app_id, user_id, bucket)
        assert 10 == len(res)

    def test_fetch_not_own_data(self):
        another_user_id = '2'
        for i in range(5):
            data = {'_key': 'k%d' % i, 'a': 10 + i, 'b': [1, 2, 3, 10 + i]}
            storage.create(app_id, another_user_id, ip, data, bucket=bucket)

        res = storage.find(app_id, another_user_id, bucket)
        assert 5 == len(res)

        id = storage.find(app_id, another_user_id, bucket, {'_key':'k1'})
        filter_opts = {'$where': 'this._id == "%s"' % id}
        res = storage.find(app_id, user_id, bucket, filter_opts)
        assert 0 == len(res)

        filter_opts = {extf.KEY: 'k1', '$where': 'this._id == "%s"' % id}
        res = storage.find(app_id, user_id, bucket, filter_opts)
        assert 0 == len(res)

        filter_opts = {extf.KEY: 'k1', '$where': 'db.entities.update({"a":-1}, {"_id":"%s"})' % id}
        storage.find(app_id, user_id, bucket, filter_opts)

        res = storage.find(app_id, another_user_id, bucket)
        assert 5 == len(res)
        
if __name__ == '__main__':
    unittest.main()