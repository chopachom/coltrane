import crud_service
import unittest

class CRUDIntegrationTestCase(unittest.TestCase):
# TODO: switch to test db in tests

    def test_create_and_read_entities(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'
        
        expected_boobs = []
        boobs_count = 3
        for i in range(boobs_count):
            data = {'test': 'test_data'}
            id = crud_service.create(app_id, user_id, data, boobs_type)
            boob = {crud_service.ENTITY_ID_KEY: id, crud_service.ENTITY_DATA_KEY: data}
            expected_boobs.append(boob)
            
        for elem in expected_boobs:
            actual_data = crud_service.read(app_id, user_id, elem[crud_service.ENTITY_ID_KEY], boobs_type)
            # asserts
            assert actual_data[crud_service.ENTITY_ID_KEY] == elem[crud_service.ENTITY_ID_KEY]
            assert actual_data[crud_service.ENTITY_DATA_KEY] == elem[crud_service.ENTITY_DATA_KEY]
        
    def test_delete_entity(self):
        app_id = '1'
        user_id = '1'
        boobs_type = 'boobs'
        
        # create 1 boob :)
        data = {'test': 'test'}
        id = crud_service.create(app_id, user_id, data, boobs_type)
        
        # try to remove this boob
        crud_service.delete(app_id, user_id, id, boobs_type)
        
        # assert boob was removed
        boob = crud_service.read(app_id, user_id, id, boobs_type)
        assert boob is None
        
    def test_access_to_another_user_entity(self):
        app_id = '1'
        user_id = '1'
        another_user_id = '2'
        boobs_type = 'boobs'
        
        # create entity
        data = {'test': 'test'}
        id = crud_service.create(app_id, user_id, data, boobs_type)
        
        # another user tries to remove entity
        with self.assertRaises(crud_service.InvalidEntityException):
            crud_service.delete(app_id, another_user_id, id, boobs_type)
            
    def test_update_entity(self):
        app_id = '1'
        user_id = '1'
        another_user_id = '2'
        boobs_type = 'boobs'
        
        # create entity
        data = {'test': 'test'}
        id = crud_service.create(app_id, user_id, data, boobs_type)
        
        # define new dict for update
        updated_data = {crud_service.ENTITY_ID_KEY: id, crud_service.ENTITY_DATA_KEY: {'updated': 'updated_data'}}
        crud_service.update(app_id, user_id, updated_data, boobs_type)
        
        # assert entity was updated
        actual_data = crud_service.read(app_id, user_id, id, boobs_type)
        assert actual_data == updated_data

if __name__ == '__main__':
    unittest.main()