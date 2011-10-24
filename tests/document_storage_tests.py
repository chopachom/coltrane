from datetime import datetime

__author__ = 'nik'

import unittest
from ds import storage
from errors import *

class DocumentStorageIntegrationTestCase(unittest.TestCase):
# TODO: switch to test db in tests

    def setUp(self):
        self.ip = '127.0.0.1'

    def test_create_and_read_entities(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'
        
        expected_boobs = []
        boobs_count = 3
        for _ in range(boobs_count):
            data = {'test': 'test_data'}
            id = storage.create(app_id, user_id, self.ip, data, boobs_type)
            data[storage.ext_fields.DOCUMENT_ID] = id
            data[storage.ext_fields.BUCKET] = boobs_type
            expected_boobs.append(data)
            
        for expected_data in expected_boobs:
            actual_data = storage.read(app_id, user_id,
                                       expected_data[storage.ext_fields.DOCUMENT_ID],
                                       boobs_type)
            del actual_data[storage.ext_fields.CREATED_AT]
            # asserts
            assert actual_data[storage.ext_fields.DOCUMENT_ID] == \
                   expected_data[storage.ext_fields.DOCUMENT_ID]
            assert actual_data == expected_data
        
    def test_delete_entity(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'
        
        # create 1 boob :)
        data = {'test': 'test'}
        id = storage.create(app_id, user_id, self.ip, data, boobs_type)
        
        # try to remove this boob
        storage.delete(app_id, user_id, self.ip, id, boobs_type)
        
        # assert boob was removed
        boob = storage.read(app_id, user_id, id, boobs_type)
        assert boob is None
        
    def test_access_to_another_user_entity(self):
        app_id = '1'
        user_id = '1'
        another_user_id = '2'
        boobs_type = 'boobs'
        
        # create entity
        data = {'test': 'test'}
        id = storage.create(app_id, user_id, self.ip, data, boobs_type)
        
        # another user tries to remove entity
        with self.assertRaises(InvalidDocumentIdError):
            storage.delete(app_id, another_user_id, self.ip, id, boobs_type)
            
    def test_update_entity(self):
        app_id = '1'
        user_id = '1'
        another_user_id = '2'
        boobs_type = 'boobs'
        
        # create entity
        data = {'test': 'test'}
        id = storage.create(app_id, user_id, self.ip, data, boobs_type)
        
        # define new dict for update
        updated_data = {'test': 'updated_data',
                        storage.ext_fields.DOCUMENT_ID: id,
                        storage.ext_fields.BUCKET:boobs_type}
        storage.update(app_id, user_id, self.ip, updated_data, boobs_type)
        
        # assert entity was updated
        actual_data = storage.read(app_id, user_id, id, boobs_type)
        del actual_data[storage.ext_fields.CREATED_AT]
        assert actual_data == updated_data
        
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
            id = storage.create(app_id, user_id, self.ip, data, boobs_type)
    
if __name__ == '__main__':
    unittest.main()