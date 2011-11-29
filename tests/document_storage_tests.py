from datetime import datetime
from appstorage.storage import ext_fields

__author__ = 'nik'

import unittest
from appstorage import storage
from api.errors import *

class DocumentStorageIntegrationTestCase(unittest.TestCase):
# TODO: switch to test db in tests

    def setUp(self):
        self.ip = '127.0.0.1'

    def tearDown(self):
        storage._entities().drop()

    def test_create_and_read_entities(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        expected_boobs = []
        boobs_count = 3
        for _ in range(boobs_count):
            data = {'test': 'test_data'}
            key = storage.create(app_id, user_id, self.ip, data, bucket=bucket)
            data[storage.ext_fields.KEY] = key
            data[storage.ext_fields.BUCKET] = bucket
            expected_boobs.append(data)

        for buck in expected_boobs:
            document = storage.get_by_key(app_id, user_id,
                bucket,
                buck[storage.ext_fields.KEY])
            del document[storage.ext_fields.CREATED_AT]
            # asserts
            assert document[storage.ext_fields.KEY] ==\
                   buck[storage.ext_fields.KEY]
            for key in document.keys():
                val1 = document[key]
                val2 = buck[key]
                assert val1 == val2

    def test_insert_documents_with_same_key(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'

        data = {'_key': '1', 'a': {'b': [1,2,3, {'c':'d'}]}}
        storage.create(app_id, user_id, self.ip, data, bucket=boobs_type)
        data2 = {'_key': '1', 'a2': {'b2': [1,2,3, {'c':'d'}]}}

        with self.assertRaises(InvalidDocumentKeyError):
            storage.create(app_id, user_id, self.ip, data2, bucket=boobs_type)
        try:
            storage.create(app_id, user_id, self.ip, data2, bucket=boobs_type)
        except InvalidDocumentKeyError as e:
            assert e.message == 'Document with key [1] already exists'
            

    def test_create_multiple_nesting_documents(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        data = {'a': {'b': [1,2,3, {'c':'d'}]}}
        key = storage.create(app_id, user_id, self.ip, data, bucket=bucket)

        d = storage.get_by_key(app_id, user_id, bucket, key)

        assert d['a'] == {'b': [1,2,3, {'c':'d'}]}
        assert d['a']['b'] == [1,2,3, {'c':'d'}]
        assert d['a']['b'][0] == 1
        assert d['a']['b'][3] == {'c':'d'}
        assert d['a']['b'][3]['c'] == 'd'


    def test_get_by_filter(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        storage.create(app_id, user_id, self.ip, {"title": "Title1", "author": "author1", "age":10, "name":"Pasha"}, bucket)
        storage.create(app_id, user_id, self.ip, {"title": "Title1", "author": "author2", "age":20, "name":"Misha"}, bucket)
        storage.create(app_id, user_id, self.ip,
            {"title": "Title1", "author": "author3", "age":15, "name":"Sasha", 'cources': {'a': {'A': 1, 'B': 2}, 'b': 10}},
                       bucket)
        storage.create(app_id, user_id, self.ip, {"title": "Title1", "author": "author4", "age":10, "name":"Dasha"}, bucket)

        docs = storage.get_by_filter(app_id, user_id, bucket, {'age': 10})
        assert len(docs) == 2

        docs = storage.get_by_filter(app_id, user_id, bucket, {'age': {'$gt': 10}})
        assert len(docs) == 2
        assert docs[0]['age'] == 20 or docs[0]['age'] == 15

        docs = storage.get_by_filter(app_id, user_id, bucket, {'age': {'$gt': 10}, 'name': 'Sasha'})
        assert len(docs) == 1
        assert docs[0]['age'] == 15

        docs = storage.get_by_filter(app_id, user_id, bucket, {'age': {'$gt': 10}, 'name': 'Sasha', 'cources.a.B': 2})
        assert len(docs) == 1
        assert docs[0]['age'] == 15

        docs = storage.get_by_filter(app_id, user_id, bucket)
        assert len(docs) == 4

        
    def test_delete_entity(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        # create 1 boob :)
        data = {'test': 'test'}
        key = storage.create(app_id, user_id, self.ip, data, bucket)

        # try to remove this boob
        storage.delete_by_filter(app_id, user_id, self.ip, bucket, {ext_fields.KEY: key})

        # assert boob was removed
        boob = storage.get_by_key(app_id, user_id, bucket, key)
        assert boob is None


    def test_delete_all_entities(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'

        # create 1 boob :)
        data = {'test': 'test1'}
        storage.create(app_id, user_id, self.ip, data, boobs_type)
        data = {'test': 'test2'}
        storage.create(app_id, user_id, self.ip, data, boobs_type)
        data = {'test': 'test3'}
        storage.create(app_id, user_id, self.ip, data, boobs_type)

        boobs = storage.get_by_filter(app_id, user_id, boobs_type)
        assert len(boobs) == 3
        # remove all boobs
        storage.delete_by_filter(app_id, user_id, self.ip, boobs_type)

        # assert all boobs were removed
        boobs = storage.get_by_filter(app_id, user_id, boobs_type)
        assert len(boobs) == 0


    def test_delete_several_by_criteria(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'

        # create 1 boob :)
        data = {'name': 'pasha'}
        storage.create(app_id, user_id, self.ip, data, boobs_type)
        data = {'name': 'sasha'}
        storage.create(app_id, user_id, self.ip, data, boobs_type)
        data = {'a': 'b'}
        storage.create(app_id, user_id, self.ip, data, boobs_type)
        data = {'name': 'pasha'}
        storage.create(app_id, user_id, self.ip, data, boobs_type)

        boobs = storage.get_by_filter(app_id, user_id, boobs_type)
        assert len(boobs) == 4
        # remove all boobs
        storage.delete_by_filter(app_id, user_id, self.ip, boobs_type, {'name': 'pasha'})

        # assert all boobs were removed
        boobs = storage.get_by_filter(app_id, user_id, boobs_type)
        assert len(boobs) == 2


    def test_access_to_another_user_entity(self):
        app_id = '1'
        user_id = '1'
        another_user_id = '2'
        bucket = 'boobs'

        # create entity
        data = {'test': 'test'}
        key = storage.create(app_id, user_id, self.ip, data, bucket)

        # another user tries to remove entity
        storage.delete_by_key(app_id, another_user_id, self.ip,
                           bucket, key)
        obj = storage.get_by_key(app_id, another_user_id, bucket, key)
        assert obj is None


    def test_update_entity(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        # create entity
        data = {'test': 'test'}
        key = storage.create(app_id, user_id, self.ip, data, bucket)

        # define new dict for update
        updated_data = {'test': 'updated_data',
                        storage.ext_fields.KEY: key,
                        storage.ext_fields.BUCKET: bucket}
        storage.update_by_key(app_id, user_id, self.ip,
                       bucket, updated_data, key)

        # assert entity was updated
        actual_data = storage.get_by_key(app_id, user_id, bucket, key)
        del actual_data[storage.ext_fields.CREATED_AT]
        for key in updated_data.keys():
            val1 = actual_data[key]
            val2 = updated_data[key]
            assert val1 == val2

    def test_update_multiple_nesting_documents(self):
        app_id = '1'
        user_id = '1'
        bucket = 'boobs'

        data = {'a': {'b': [1,2,3, {'c':'d'}]}}
        key = storage.create(app_id, user_id, self.ip, data, bucket=bucket)
        update_data = {'a': {'b': 'c'}, 'addition': [1,2,3]}
        storage.update_by_key(app_id, user_id, self.ip, bucket,
                       update_data, key)

        d = storage.get_by_key(app_id, user_id, bucket, key)

        assert d['a'] == {'b': 'c'}
        assert d['a']['b'] == 'c'
        assert d['addition'] == [1,2,3]


if __name__ == '__main__':
    unittest.main()