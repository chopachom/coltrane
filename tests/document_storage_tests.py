from datetime import datetime

__author__ = 'nik'

import unittest
from ds import storage
from errors import *

class DocumentStorageIntegrationTestCase(unittest.TestCase):
# TODO: switch to test db in tests

    def setUp(self):
        self.ip = '127.0.0.1'

    def tearDown(self):
        storage._entities.drop()

    def test_create_and_read_entities(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'

        expected_boobs = []
        boobs_count = 3
        for _ in range(boobs_count):
            data = {'test': 'test_data'}
            key = storage.create(app_id, user_id, self.ip, data, bucket=boobs_type)
            data[storage.ext_fields.DOCUMENT_KEY] = key
            data[storage.ext_fields.BUCKET] = boobs_type
            expected_boobs.append(data)

        for boob in expected_boobs:
            document = storage.find_by_key(app_id, user_id,
                boob[storage.ext_fields.DOCUMENT_KEY],
                bucket=boobs_type)
            del document[storage.ext_fields.CREATED_AT]
            # asserts
            assert document[storage.ext_fields.DOCUMENT_KEY] ==\
                   boob[storage.ext_fields.DOCUMENT_KEY]
            for key in document.keys():
                val1 = document[key]
                val2 = boob[key]
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
        boobs_type = 'boobs'

        data = {'a': {'b': [1,2,3, {'c':'d'}]}}
        key = storage.create(app_id, user_id, self.ip, data, bucket=boobs_type)

        d = storage.find_by_key(app_id, user_id, key, boobs_type)

        assert d['a'] == {'b': [1,2,3, {'c':'d'}]}
        assert d['a']['b'] == [1,2,3, {'c':'d'}]
        assert d['a']['b'][0] == 1
        assert d['a']['b'][3] == {'c':'d'}
        assert d['a']['b'][3]['c'] == 'd'


    def test_delete_entity(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'

        # create 1 boob :)
        data = {'test': 'test'}
        key = storage.create(app_id, user_id, self.ip, data, boobs_type)

        # try to remove this boob
        storage.delete_by_key(app_id, user_id, self.ip, key, boobs_type)

        # assert boob was removed
        boob = storage.find_by_key(app_id, user_id, key, boobs_type)
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

        boobs = storage.get_all(app_id, user_id, boobs_type)
        assert len(boobs) == 3
        # remove all boobs
        storage.delete_several(app_id, user_id, self.ip, boobs_type)

        # assert all boobs were removed
        boobs = storage.get_all(app_id, user_id, boobs_type)
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

        boobs = storage.get_all(app_id, user_id, boobs_type)
        assert len(boobs) == 4
        # remove all boobs
        storage.delete_several(app_id, user_id, self.ip, boobs_type, {'name': 'pasha'})

        # assert all boobs were removed
        boobs = storage.get_all(app_id, user_id, boobs_type)
        assert len(boobs) == 2


    def test_access_to_another_user_entity(self):
        app_id = '1'
        user_id = '1'
        another_user_id = '2'
        boobs_type = 'boobs'

        # create entity
        data = {'test': 'test'}
        key = storage.create(app_id, user_id, self.ip, data, boobs_type)

        # another user tries to remove entity
        with self.assertRaises(DocumentNotFoundError):
            storage.delete_by_key(app_id, another_user_id, self.ip, key, boobs_type)


    def test_update_entity(self):
        app_id = '1'
        user_id = '1'
        another_user_id = '2'
        boobs_type = 'boobs'

        # create entity
        data = {'test': 'test'}
        key = storage.create(app_id, user_id, self.ip, data, boobs_type)

        # define new dict for update
        updated_data = {'test': 'updated_data',
                        storage.ext_fields.DOCUMENT_KEY: key,
                        storage.ext_fields.BUCKET: boobs_type}
        storage.update(app_id, user_id, self.ip, updated_data, boobs_type)

        # assert entity was updated
        actual_data = storage.find_by_key(app_id, user_id, key, boobs_type)
        del actual_data[storage.ext_fields.CREATED_AT]
        for key in updated_data.keys():
            val1 = actual_data[key]
            val2 = updated_data[key]
            assert val1 == val2

    def test_update_multiple_nesting_documents(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'

        data = {'a': {'b': [1,2,3, {'c':'d'}]}}
        key = storage.create(app_id, user_id, self.ip, data, bucket=boobs_type)
        update_data = {'_key':key, 'a': {'b': 'c'}, 'addition': [1,2,3]}
        storage.update(app_id, user_id, self.ip, update_data, bucket=boobs_type)

        d = storage.find_by_key(app_id, user_id, key, boobs_type)

        assert d['a'] == {'b': 'c'}
        assert d['a']['b'] == 'c'
        assert d['addition'] == [1,2,3]


    def test_create_with_not_allowed_key(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'

        # create entity with not allowed key
        data = {
            'test': 'test',
            storage.int_fields.BUCKET: '__bucket__' # not allowed key
        }
        with self.assertRaises(InvalidDocumentError):
            storage.create(app_id, user_id, self.ip, data, boobs_type)

if __name__ == '__main__':
    unittest.main()