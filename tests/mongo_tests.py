import unittest
from ds import storage
from ds.storage import ext_fields

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
        storage._entities.drop()

    def test_security_when_where_used(self):
        filter_opts = {'a': {'$gt': 5}, '$where': 'db.entities.drop()'}

        with self.assertRaises(Exception):
            storage.get_by_filter(app_id, user_id, bucket, filter_opts)

        res = storage.get_by_filter(app_id, user_id, bucket)
        assert 10 == len(res)

        filter_opts = {'$where': 'db.dropDatabase()'}
        storage.get_by_filter(app_id, user_id, bucket, filter_opts)

        res = storage.get_by_filter(app_id, user_id, bucket)
        assert 10 == len(res)

        with self.assertRaises(Exception):
            storage.get_by_filter(app_id, user_id, bucket, {"$where": "db.entities.drop()"})
        res = storage.get_by_filter(app_id, user_id, bucket)
        assert 10 == len(res)

    def test_fetch_not_own_data(self):
        another_user_id = '2'
        for i in range(5):
            data = {'_key': 'k%d' % i, 'a': 10 + i, 'b': [1, 2, 3, 10 + i]}
            storage.create(app_id, another_user_id, ip, data, bucket=bucket)

        res = storage.get_by_filter(app_id, another_user_id, bucket)
        assert 5 == len(res)

        id = storage._document_id(app_id, another_user_id, bucket, 'k1')
        filter_opts = {'$where': 'this._id == "%s"' % id}
        res = storage.get_by_filter(app_id, user_id, bucket, filter_opts)
        assert 0 == len(res)

        filter_opts = {ext_fields.KEY: 'k1', '$where': 'this._id == "%s"' % id}
        res = storage.get_by_filter(app_id, user_id, bucket, filter_opts)
        assert 0 == len(res)

        filter_opts = {ext_fields.KEY: 'k1', '$where': 'db.entities.update({"a":-1}, {"_id":"%s"})' % id}
        storage.get_by_filter(app_id, user_id, bucket, filter_opts)

        res = storage.get_by_filter(app_id, another_user_id, bucket)
        assert 5 == len(res)
        
if __name__ == '__main__':
    unittest.main()