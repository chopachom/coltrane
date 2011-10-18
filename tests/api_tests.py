import unittest
from app import create_app
from db import crud
from api import api_v1

__author__ = 'pshkitin'

API_V1 = '/v1'
class ApiTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app(modules=((api_v1, API_V1),), exts=(crud,), dict_config=dict(
            DEBUG=False,
            TESTING=True
        ))
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_getAll_request(self):
        rv = self.app.get(API_V1 + '/books')
        print "Get all: " + rv.data
        #assert 'No entries here so far' in rv.data

    def test_getById_request(self):
        rv = self.app.get(API_V1 + '/books/1')
        print "Get by id: " + rv.data

    def test_post_request(self):
        rv = self.app.post(API_V1 + '/books', data=dict(
            data='{"id":3, "title": "Title3", "author": "Pasha Shkitin"}'
        ), follow_redirects=True)
        print "Post1: " + rv.data

    def test_success_delete_request(self):
        rv = self.app.delete(API_V1 + '/books/2')
        print "Success delete: " + rv.data

    def test_fail_delete_request(self):
        rv = self.app.delete(API_V1 + '/books/4')
        print "Fail delete: " + rv.data

    def test_put_request(self):
        rv = self.app.put(API_V1 + '/books', data=dict(
            data='{"id":2, "title": "Title3", "author": "Vasya Shkitin"}'
        ), follow_redirects=True)
        print 'Put1: ' + rv.data
    
if __name__ == '__main__':
    unittest.main()