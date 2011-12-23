import copy

__author__ = 'nik'

import unittest
from pymongo.connection import Connection

from coltrane.rest import config
from coltrane.appstorage.storage import AppdataStorage, _from_external_to_internal, intf
from coltrane.appstorage.storage import extf


test_database   = config.TestConfig.MONGODB_DATABASE
test_collection = config.TestConfig.APPDATA_COLLECTION
c = Connection()
storage = AppdataStorage(c[test_database][test_collection])


class DocumentStorageIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self.ip = '127.0.0.1'


    def tearDown(self):
        storage.entities.drop()

    def test_create_and_read_entities(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        expected_boobs = []
        boobs_count = 3
        for _ in range(boobs_count):
            data = {'test': 'test_data'}
            key = storage.create(app_id, user_id, bucket, self.ip, data)
            data[extf.KEY] = key
            data[extf.BUCKET] = bucket
            expected_boobs.append(data)

        for buck in expected_boobs:
            document = storage.get(app_id, user_id, bucket, key=buck[extf.KEY])
            del document[extf.CREATED_AT]
            # asserts
            assert document[extf.KEY] ==\
                   buck[extf.KEY]
            for key in document.keys():
                val1 = document[key]
                val2 = buck[key]
                assert val1 == val2


    def test_create_multiple_nesting_documents(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        data = {'a': {'b': [1,2,3, {'c':'d'}]}}
        key = storage.create(app_id, user_id, bucket, self.ip, data)

        d = storage.get(app_id, user_id, bucket, key=key)

        assert d['a'] == {'b': [1,2,3, {'c':'d'}]}
        assert d['a']['b'] == [1,2,3, {'c':'d'}]
        assert d['a']['b'][0] == 1
        assert d['a']['b'][3] == {'c':'d'}
        assert d['a']['b'][3]['c'] == 'd'


    def test_find(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        storage.create(app_id, user_id, bucket, self.ip, {"title": "Title1", "author": "author1", "age":10, "name":"Pasha"})
        storage.create(app_id, user_id, bucket, self.ip, {"title": "Title1", "author": "author2", "age":20, "name":"Misha"})
        storage.create(app_id, user_id, bucket, self.ip,
            {"title": "Title1", "author": "author3", "age":15, "name":"Sasha", 'cources': {'a': {'A': 1, 'B': 2}, 'b': 10}})
        storage.create(app_id, user_id, bucket, self.ip, {"title": "Title1", "author": "author4", "age":10, "name":"Dasha"})

        docs = storage.find(app_id, user_id, bucket, {'age': 10})
        assert len(docs) == 2

        docs = storage.find(app_id, user_id, bucket, {'age': {'$gt': 10}})
        assert len(docs) == 2
        assert docs[0]['age'] == 20 or docs[0]['age'] == 15

        docs = storage.find(app_id, user_id, bucket, {'age': {'$gt': 10}, 'name': 'Sasha'})
        assert len(docs) == 1
        assert docs[0]['age'] == 15

        docs = storage.find(app_id, user_id, bucket, {'age': {'$gt': 10}, 'name': 'Sasha', 'cources.a.B': 2})
        assert len(docs) == 1
        assert docs[0]['age'] == 15

        docs = storage.find(app_id, user_id, bucket)
        assert len(docs) == 4

        
    def test_delete_entity(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        # create 1 boob :)
        data = {'test': 'test'}
        key = storage.create(app_id, user_id, bucket, self.ip, data)

        # try to remove this boob
        storage.delete(app_id, user_id, bucket, self.ip, filter_opts={extf.KEY: key})

        # assert boob was removed
        boob = storage.get(app_id, user_id, bucket, key)
        assert boob is None


    def test_delete_all_entities(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'

        # create 1 boob :)
        data = {'test': 'test1'}
        storage.create(app_id, user_id, boobs_type, self.ip, data)
        data = {'test': 'test2'}
        storage.create(app_id, user_id, boobs_type, self.ip, data)
        data = {'test': 'test3'}
        storage.create(app_id, user_id, boobs_type, self.ip, data)

        boobs = storage.find(app_id, user_id, boobs_type)
        assert len(boobs) == 3
        # remove all boobs
        storage.delete(app_id, user_id, boobs_type, self.ip)

        # assert all boobs were removed
        boobs = storage.find(app_id, user_id, boobs_type)
        assert len(boobs) == 0


    def test_delete_several_by_criteria(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'

        # create 1 boob :)
        data = {'name': 'pasha'}
        storage.create(app_id, user_id, boobs_type, self.ip, data)
        data = {'name': 'sasha'}
        storage.create(app_id, user_id, boobs_type, self.ip, data)
        data = {'a': 'b'}
        storage.create(app_id, user_id, boobs_type, self.ip, data)
        data = {'name': 'pasha'}
        storage.create(app_id, user_id, boobs_type, self.ip, data)

        boobs = storage.find(app_id, user_id, boobs_type)
        assert len(boobs) == 4
        # remove all boobs
        storage.delete(app_id, user_id, boobs_type, self.ip, filter_opts={'name': 'pasha'})

        # assert all boobs were removed
        boobs = storage.find(app_id, user_id, boobs_type)
        assert len(boobs) == 2


    def test_access_to_another_user_entity(self):
        app_id = '1'
        user_id = '1'
        another_user_id = '2'
        bucket = 'boobs'

        # create entity
        data = {'test': 'test'}
        key = storage.create(app_id, user_id, bucket, self.ip, data)

        # another user tries to remove entity
        storage.delete(app_id, another_user_id, bucket, self.ip, key=key)
        obj = storage.get(app_id, another_user_id, bucket, key)
        assert obj is None


    def test_update_entity(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        # create entity
        data = {'test': 'test'}
        key = storage.create(app_id, user_id, bucket, self.ip, data)

        # define new dict for update
        updated_data = {'test': 'updated_data',
                        extf.KEY: key,
                        extf.BUCKET: bucket}
        storage.update(app_id, user_id, bucket, self.ip,
            copy.deepcopy(updated_data), key=key)

        # assert entity was updated
        actual_data = storage.get(app_id, user_id, bucket, key)
        del actual_data[extf.CREATED_AT]
        for key in updated_data.keys():
            val1 = actual_data[key]
            val2 = updated_data[key]
            assert val1 == val2

    def test_update_multiple_nesting_documents(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        data = {'a': {'b': [1,2,3, {'c':'d'}]}}
        key = storage.create(app_id, user_id, bucket, self.ip, data)
        update_data = {'a': {'b': 'c'}, 'addition': [1,2,3]}
        storage.update(app_id, user_id, bucket, self.ip,
                       update_data, key=key)

        d = storage.get(app_id, user_id, bucket, key)

        assert d['a'] == {'b': 'c'}
        assert d['a']['b'] == 'c'
        assert d['addition'] == [1,2,3]


    def test_from_int_to_ext(self):
        d = {extf.KEY:'key', 'a':{'b':[{'a':10},10,
                {extf.KEY:15, extf.BUCKET:'buck'}, {extf.CREATED_AT:'10.10.2010'}]}}
        res = _from_external_to_internal(d, 'a', 'b', 'c')
        assert res == {'a':
                           {'b':
                              [
                                 {'a': 10}, 10,
                                 {intf.BUCKET: 'buck', intf.ID: 'a|b|c|15'},
                                 {intf.CREATED_AT: '10.10.2010'}
                              ]
                           },
                       '_id': 'a|b|c|key'}


if __name__ == '__main__':
    unittest.main()